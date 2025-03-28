from flask import Flask, render_template, request, redirect
import pymysql
from datetime import datetime, timedelta
import csv

app = Flask(__name__)

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='31718750',  # ← 본인 비번
    db='baby_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def calculate_milestones(birth_date):
    birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
    milestones = {
        'D+100': birth + timedelta(days=100),
        '예방접종 시기': birth + timedelta(days=60),
        '이유식 시작 시기': birth + timedelta(weeks=26),
        '옹알이 시기': f"{birth + timedelta(weeks=6)} ~ {birth + timedelta(weeks=24)}",
        '걸음마 시기': f"{birth + timedelta(weeks=52)} ~ {birth + timedelta(weeks=78)}",
    }
    return milestones

def calculate_months(birth_date):
    birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
    today = datetime.today()
    months = (today.year - birth.year) * 12 + (today.month - birth.month)
    return months

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    birth_date = request.form['birth_date']
    birth_time = request.form['birth_time']
    blood_type = request.form['blood_type']
    weight = request.form['weight']
    parent_name = request.form['parent_name']

    with conn.cursor() as cursor:
        sql = """
            INSERT INTO baby_info (name, birth_date, birth_time, blood_type, weight, parent_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (name, birth_date, birth_time, blood_type, weight, parent_name))
        conn.commit()

    milestones = calculate_milestones(birth_date)

    return render_template('result.html', name=name, milestones=milestones)

@app.route('/recipe/<birth_date>')
def recipe(birth_date):
    months = calculate_months(birth_date)
    selected_recipes = []

    with open('recipes.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['month']) <= months:
                selected_recipes.append({
                    'title': row['title'],
                    'description': row['description'],
                    'video': row['video'],
                    'image': row['image'],
                    'caution': row['caution']
                })

    return render_template('recipe.html', recipes=selected_recipes, months=months)




@app.route('/babies')
def baby_list():
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, birth_date FROM baby_info ORDER BY created_at DESC")
        babies = cursor.fetchall()
    return render_template('babies.html', babies=babies)

@app.route('/baby/<int:baby_id>')
def show_baby(baby_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM baby_info WHERE id = %s", (baby_id,))
        baby = cursor.fetchone()

    if not baby:
        return "해당 아기를 찾을 수 없습니다."

    milestones = calculate_milestones(baby['birth_date'])
    months = calculate_months(baby['birth_date'])
    feeding_guide = get_feeding_guide(months)
    vaccines = get_vaccine_schedule(baby['birth_date'])

    return render_template(
        'result.html',
        name=baby['name'],
        milestones=milestones,
        birth_date=baby['birth_date'],
        months=months,
        feeding_guide=feeding_guide,
        vaccines=vaccines
    )


@app.route('/map')
def map_page():
    return render_template('map.html')


def get_feeding_guide(months):
    if months < 6:
        return "모유 또는 분유만 섭취 가능해요."
    elif 6 <= months <= 7:
        return "초기 이유식을 시작할 수 있어요. (쌀미음, 단호박미음 등)"
    elif 8 <= months <= 9:
        return "중기 이유식을 먹을 시기예요. (감자죽, 채소죽 등)"
    elif 10 <= months <= 11:
        return "후기 이유식을 먹을 수 있어요. (진밥, 고기반찬 등)"
    else:
        return "잘게 자른 일반식으로 넘어갈 수 있어요. (소프트 고형식)"

def get_vaccine_schedule(birth_date):
    birth = datetime.strptime(str(birth_date), "%Y-%m-%d")
    today = datetime.today()
    schedule = []

    vaccines = [
        ("BCG", 0),
        ("HepB 1차", 0),
        ("HepB 2차", 1),
        ("DTP 1차", 2),
        ("DTP 2차", 4),
        ("폐렴구균 1차", 2),
        ("폐렴구균 2차", 4)
    ]

    for name, month in vaccines:
        due_date = birth + timedelta(weeks=month*4)
        days_left = (due_date - today).days

        if days_left < 0:
            status = f"✅ 완료 시기 지남 (예정일: {due_date.date()})"
        elif days_left <= 7:
            status = f"⚠️ {days_left}일 남음 (예정일: {due_date.date()})"
        else:
            status = f"예정일: {due_date.date()}"

        schedule.append({
            'name': name,
            'due_date': due_date.date(),
            'status': status
        })

    return schedule



if __name__ == '__main__':
    app.run(debug=True)
