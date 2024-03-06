from fastapi import FastAPI, HTTPException, UploadFile, Depends, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from csv_app.sql_app import models
from csv_app.sql_app.database import SessionLocal, engine
from starlette.responses import StreamingResponse
import io

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message"}


@app.post("/parsefile/")
def parse_file(file: UploadFile):
    resp = csv_parser(file)
    return resp


@app.post("/savefile/")
def save_file(file: UploadFile, db: Session = Depends(get_db)):
    data = csv_parser(file)

    for user in data['info']:
        db_user = models.User(**user)

        db.add(db_user)
    db.commit()
    return db_user


def csv_parser(file):
    if not file:
        raise HTTPException(status_code=404, detail={'error': 'No file attached'})
    data = []

    lines = file.file.readlines()
    if not lines:
        raise HTTPException(status_code=404, detail={'error': 'File is empty'})
    categories = {
        "category",
        "firstname",
        "lastname",
        "email",
        "gender",
        "birthDate"
    }
    header_info = lines.pop(0).strip().decode('utf-8').split(',')
    if not set(header_info).issubset(categories):
        raise HTTPException(status_code=404, detail={
            'error': 'Here is no header or file missing fields',
            'header': header_info
        })
    for line in lines:
        line_info = line.strip().decode('utf-8').split(',')
        data.append(line_info_to_dict(header_info, line_info))
    return {
        'header': header_info,
        'info': data
    }


def line_info_to_dict(header, line_info):
    result_dict = {}

    for key, value in zip(header, line_info):
        if key == 'birthDate':
            value = datetime.strptime(value, '%Y-%m-%d')
        result_dict[key] = value
    return result_dict


@app.get("/users/")
def filter_users(
    response: Response,
    category: str = Query(None, title="Category"),
    gender: str = Query(None, title="Gender"),
    dob: str = Query(None, title="Date of Birth (YYYY-MM-DD)"),
    age: int = Query(None, title="Age"),
    start_age: int = Query(None, title="Start Age"),
    end_age: int = Query(None, title="End Age"),
    file: bool = False
):
    categories = {
        "category",
        "firstname",
        "lastname",
        "email",
        "gender",
        "birthDate"
    }
    filters = []

    if category:
        filters.append(models.User.category == category)
    if gender:
        filters.append(models.User.gender == gender)
    if dob:
        filters.append(models.User.birthDate == dob)
    if age:
        current_date = datetime.now().date()
        dob = current_date - timedelta(days=365 * age)
        filters.append(models.User.birthDate <= dob)
    if start_age and end_age:
        current_date = datetime.now().date()
        start_dob = current_date - timedelta(days=365 * end_age)
        end_dob = current_date - timedelta(days=365 * start_age)
        filters.append(models.User.birthDate.between(start_dob, end_dob))

    with SessionLocal() as session:
        if filters:
            users = session.query(models.User).filter(*filters).all()
        else:
            users = session.query(models.User).all()

        # If file True return csv file else return users data
        if file:
            obj_lst = [{x: getattr(user, x) for x in categories} for user in users]
            csv_data = dict_to_csv(obj_lst)
            headers = {
                "Content-Disposition": "attachment; filename=export.csv",
                "Content-Type": "text/csv",
            }

            return StreamingResponse(io.BytesIO(csv_data.encode('utf-8')), headers=headers)

        return users


def dict_to_csv(data):
    # Get the headers from the dictionary keys
    headers = list(data[0].keys())

    # Write headers to CSV string
    csv_string = ','.join(headers) + '\n'

    # Write data rows to CSV string
    for row in data:
        csv_string += ','.join(str(row[header]) for header in headers) + '\n'

    return csv_string
