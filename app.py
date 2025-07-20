import random
import math
import sqlite3
import streamlit as st

# Sayfa seçim menüsü
page = st.sidebar.radio("Sayfalar", ["Tabaka Bilgileri", "Parça Bilgileri", "Sonuç"])

# Tabakalar için sorular
if page == "Tabaka Bilgileri":
    st.title("Tabaka Bilgileri")
    st.write("Lütfen sahip olduğunuz **tabaka** bilgilerini girin.")

    tabaka_sayisi = st.number_input('Kaç Farklı Boy Tabakanız Var?', min_value=1, max_value=10, value=3)

    tabakalar = []
    for i in range(tabaka_sayisi):
        st.subheader(f"Tabaka {i+1} Bilgileri")
        tabaka_uzunluk = st.number_input(f"Tabaka {i+1} Uzunluğu (mm)", min_value=100, value=3000)
        tabaka_genislik = st.number_input(f"Tabaka {i+1} Genişliği (mm)", min_value=100, value=1500)
        tabaka_kalinlik = st.number_input(f"Tabaka {i+1} Kalınlığı (mm)", min_value=1, value=5)
        adet = st.number_input(f"Tabaka {i+1} Adet", min_value=1, value=3)

        tabakalar.append({
            "uzunluk": tabaka_uzunluk,
            "genislik": tabaka_genislik,
            "kalinlik": tabaka_kalinlik,
            "adet": adet
        })

    # Butonla geçişi sağla
    if st.button('İleri'):
        st.session_state.tabakalar = tabakalar
        st.experimental_rerun()

# Parçalar için sorular
if page == "Parça Bilgileri":
    st.title("Parça Bilgileri")
    st.write("Lütfen **parça** bilgilerini girin.")
    
    if 'tabakalar' not in st.session_state:
        st.write("Lütfen önce tabaka bilgilerini girin.")
    else:
        parca_sayisi = st.number_input('Kaç Farklı Parça Bilgisi Girilecek?', min_value=1, max_value=10, value=3)

        parcalar = []
        for i in range(parca_sayisi):
            st.subheader(f"Parça {i+1} Bilgileri")
            parca_uzunluk = st.number_input(f"Parça {i+1} Uzunluğu (mm)", min_value=1, value=900)
            parca_genislik = st.number_input(f"Parça {i+1} Genişliği (mm)", min_value=1, value=300)
            parca_kalinlik = st.number_input(f"Parça {i+1} Kalınlığı (mm)", min_value=1, value=5)
            adet_parca = st.number_input(f"Parça {i+1} Adet", min_value=1, value=20)

            parcalar.append({
                "uzunluk": parca_uzunluk,
                "genislik": parca_genislik,
                "kalinlik": parca_kalinlik,
                "adet": adet_parca
            })

        # Butonla geçişi sağla
        if st.button('İleri'):
            st.session_state.parcalar = parcalar
            st.experimental_rerun()

# Sonuç sayfası
if page == "Sonuç":
    st.title("En İyi Yerleşim Çözümü")
    
    if 'parcalar' not in st.session_state or 'tabakalar' not in st.session_state:
        st.write("Lütfen önce tabaka ve parça bilgilerini girin.")
    else:
        # Simüle Tavlama Algoritması
        best_solution = simule_tavlama(st.session_state.parcalar, st.session_state.tabakalar, max_iter=50, initial_temp=100, cooling_rate=0.99)

        # Atık ve etkinlik hesaplamalarını yapalım
        waste = calculate_waste(best_solution)
        efficiency = calculate_efficiency(best_solution, st.session_state.tabakalar)
        cost = calculate_cost(best_solution)

        # Sonuçları Streamlit ile göster
        st.write("**En İyi Yerleşim Çözümü:**")
        for parca, tabaka in best_solution:
            st.write(f"Parça: {parca['uzunluk']}x{parca['genislik']} mm, Tabaka: {tabaka['uzunluk']}x{tabaka['genislik']} mm")

        st.write(f"**Atık Alanı:** {waste} birim²")
        st.write(f"**Tabakaların Etkinliği:** {efficiency:.2f}%")
        st.write(f"**Toplam Maliyet:** {cost} birim")

# Simüle Tavlama Algoritması
def simule_tavlama(parcalar, tabakalar, max_iter=1000, initial_temp=100, cooling_rate=0.99):
    current_solution = generate_initial_solution(parcalar, tabakalar)
    current_cost = calculate_cost(current_solution)
    
    best_solution = current_solution
    best_cost = current_cost
    
    temp = initial_temp
    for i in range(max_iter):
        new_solution = generate_new_solution(current_solution)
        new_cost = calculate_cost(new_solution)
        
        if new_cost < current_cost or random.uniform(0, 1) < math.exp((current_cost - new_cost) / temp):
            current_solution = new_solution
            current_cost = new_cost
        
        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost
        
        temp *= cooling_rate
    
    return best_solution

def generate_initial_solution(parcalar, tabakalar):
    return [(random.choice(parcalar), random.choice(tabakalar)) for _ in range(len(parcalar))]

def generate_new_solution(solution):
    new_solution = solution[:]
    i = random.randint(0, len(solution) - 1)
    new_solution[i] = (random.choice(parcalar), random.choice(tabakalar))
    return new_solution

def calculate_cost(solution):
    cost = 0
    for parca, tabaka in solution:
        cost += (tabaka['uzunluk'] * tabaka['genislik']) - (parca['uzunluk'] * parca['genislik'])
    return cost

# Etkinlik Hesaplama
def calculate_efficiency(solution, tabakalar):
    total_used_area = 0
    total_area = 0
    
    for parca, tabaka in solution:
        total_area += tabaka['uzunluk'] * tabaka['genislik']
        total_used_area += parca['uzunluk'] * parca['genislik']
    
    efficiency = (total_used_area / total_area) * 100
    return efficiency

# Atık Alanı Hesaplama
def calculate_waste(solution):
    total_waste = 0
    for parca, tabaka in solution:
        waste = (tabaka['uzunluk'] * tabaka['genislik']) - (parca['uzunluk'] * parca['genislik'])
        total_waste += waste
    return total_waste

# Maliyet Hesaplama
def calculate_cost(solution, material_cost_per_unit=1, labor_cost_per_unit=0.5):
    total_cost = 0
    for parca, tabaka in solution:
        material_cost = parca['uzunluk'] * parca['genislik'] * material_cost_per_unit
        labor_cost = parca['uzunluk'] * parca['genislik'] * labor_cost_per_unit
        total_cost += material_cost + labor_cost
    return total_cost
