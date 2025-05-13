import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# 생애주기 계산 함수
def calculate_milestones(birth_date):
    milestones = {
        'D+100': birth_date + timedelta(days=100),
        '예방접종 시기': birth_date + timedelta(days=60),
        '이유식 시작 시기': birth_date + timedelta(weeks=26),
        '옹알이 시기': f"{birth_date + timedelta(weeks=6)} ~ {birth_date + timedelta(weeks=24)}",
        '걸음마 시기': f"{birth_date + timedelta(weeks=52)} ~ {birth_date + timedelta(weeks=78)}"
    }
    return milestones

# 생후 개월 수 계산
def calculate_months(birth_date):
    today = datetime.today()
    return (today.year - birth_date.year) * 12 + (today.month - birth_date.month)

# 이유식 추천
def show_recipes():
    st.subheader("🍚 이유식 레시피 전체 보기")
    try:
        df = pd.read_csv("recipes.csv")
        st.text(f"✅ 총 {len(df)}개의 레시피를 불러왔습니다.")

        for _, row in df.iterrows():
            with st.container():
                st.markdown(f"### {row['title']} ({row['month']}개월~)")
                st.image(f"images/{row['image']}", use_column_width=True)
                st.write(f"**설명:** {row['description']}")
                st.video(row['video'])
                st.warning(f"⚠️ 주의사항: {row['caution']}")
                st.markdown("---")

    except FileNotFoundError:
        st.error("📁 recipes.csv 파일이 존재하지 않습니다.")
    except Exception as e:
        st.error(f"❌ 레시피 로딩 중 오류: {e}")


# 예방접종 스케줄

def get_vaccine_schedule(birth_date):
    today = datetime.today().date()
    vaccines = [
        ("BCG(결핵 예방 접종)", 0),
        ("HepB(B형 감염주사) 1차", 0),
        ("HepB(B형 감염주사) 2차", 1),
        ("DTP(디프테리아, 파상풍, 백일해) 1차", 2),
        ("DTP(디프테리아, 파상풍, 백일해) 2차", 4),
        ("포마우루군 1차", 2),
        ("포마우루군 2차", 4)
    ]
    schedule = []
    for name, month in vaccines:
        due_date = birth_date + timedelta(weeks=month * 4)
        days_left = (due_date - today).days
        if days_left < 0:
            status = f"✅ 완료 시기 지남 ({due_date})"
        elif days_left <= 7:
            status = f"⚠️ {days_left}일 남음 ({due_date})"
        else:
            status = f"{due_date} 예정"
        schedule.append({"접종명": name, "예정일": due_date, "상태": status})
    return pd.DataFrame(schedule)

# 소아과 지도
# def show_map(search_keyword="서울 강남구 소아과"):
#     st.subheader("🏥 주변 소아과 지도")

#     st.text(f"🔍 '{search_keyword}' 위치 검색 중...")
#     geolocator = Nominatim(user_agent="babyapp")
#     location = geolocator.geocode(search_keyword)

#     if not location:
#         st.error(f"❌ '{search_keyword}' 위치를 찾을 수 없습니다.")
#         return

#     st.success(f"✅ 위치 찾음: {location.latitude}, {location.longitude}")

#     m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15)
#     folium.Marker(
#         [location.latitude, location.longitude],
#         tooltip=search_keyword,
#         popup="🔍 검색 위치"
#     ).add_to(m)

#     st_folium(m, width=700, height=500)



# 메인 UI
st.title("🍼 신생아 유아 정보 입력")
name = st.text_input("아기 이름")
birth_date = st.date_input("생년월일")

if st.button("생애 주기 확인"):
    if name and birth_date:
        milestones = calculate_milestones(birth_date)
        st.subheader(f"{name}의 주요 생애 일정")
        for k, v in milestones.items():
            st.write(f"- {k}: {v}")

        months = calculate_months(birth_date)
        show_recipes()

        df_vaccine = get_vaccine_schedule(birth_date)
        st.subheader("💉 예방접종 스케줄")
        st.dataframe(df_vaccine, use_container_width=True)
    else:
        st.warning("이름과 생년월일을 모두 입력해주세요.")

# 지도 표시 UI
# with st.expander("📍 소아과 지도 보기"):
#     keyword = st.text_input("지역명 또는 병원 검색어", value="서울 강남구 소아과", key="map_search")

#     if "show_map" not in st.session_state:
#         st.session_state.show_map = False

#     if st.button("지도 보기"):
#         st.session_state.show_map = True

#     if st.session_state.show_map:
#         show_map(keyword)