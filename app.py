import random
import math
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Parçalar ve Tabakalar Verisi
parcalar = [
    {"uzunluk": 900, "genislik": 300, "kalinlik": 5, "adet": 20},
    {"uzunluk": 780, "genislik": 180, "kalinlik": 3, "adet": 12},
    {"uzunluk": 340, "genislik": 550, "kalinlik": 3, "adet": 22},
]

tabakalar = [
    {"uzunluk": 3000, "genislik": 1500, "kalinlik": 5, "adet": 3},
    {"uzunluk": 1500, "genislik": 1000, "kalinlik": 3, "adet": 2},
    {"uzunluk": 1000, "genislik": 2000, "kalinlik": 3, "adet": 1},
]

# Veritabanı Bağlantısı
def create_db():
    conn = sqlite3.connect('kesim_optimizasyonu.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS kesim_verileri (
                        id INTEGER PRIMARY KEY,
                        parca_uzunluk REAL,
                        parca_genislik REAL,
                        parca_kalinlik REAL,
                        tabaka_uzunluk REAL,
                        tabaka_genislik REAL,
                        tabaka_kalinlik REAL,
                        adet INTEGER)''')
    conn.commit()
    conn.close()

# Veritabanına Veri Ekleme
def insert_data(parca, tabaka, adet):
    conn = sqlite3.connect('kesim_optimizasyonu.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO kesim_verileri (parca_uzunluk, parca_genislik, parca_kalinlik, 
                                                   tabaka_uzunluk, tabaka_genislik, tabaka_kalinlik, adet) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (parca['uzunluk'], parca['genislik'], parca['kalinlik'],
                    tabaka['uzunluk'], tabaka['genislik'], tabaka['kalinlik'], adet))
    conn.commit()
    conn.close()

# Veritabanından Veri Çekme
def get_data():
    conn = sqlite3.connect('kesim_optimizasyonu.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kesim_verileri')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

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

# Genetik Algoritma için yardımcı fonksiyonlar
def generate_initial_population(parcalar, tabakalar, pop_size=100):
    population = []
    for _ in range(pop_size):
        solution = generate_initial_solution(parcalar, tabakalar)
        population.append(solution)
    return population

def fitness(solution):
    cost = 0
    for parca, tabaka in solution:
        cost += (tabaka['uzunluk'] * tabaka['genislik']) - (parca['uzunluk'] * parca['genislik'])
    return cost

def selection(population):
    selected = random.choices(population, k=2)
    return selected

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1)-1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutation(solution, mutation_rate=0.1):
    if random.random() < mutation_rate:
        i = random.randint(0, len(solution) - 1)
        solution[i] = (random.choice(parcalar), random.choice(tabakalar))
    return solution

def evolve(population, generations=100, mutation_rate=0.1):
    for gen in range(generations):
        population.sort(key=lambda x: fitness(x))
        new_population = []
        while len(new_population) < len(population):
            parent1, parent2 = selection(population)
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutation(child1, mutation_rate))
            new_population.append(mutation(child2, mutation_rate))
        population = new_population
    return population[0]

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

# Görselleştirme
def visualize_layout(parcalar, tabakalar, yerlesimler):
    fig, ax = plt.subplots()
    ax.set_xlim(0, 3000)
    ax.set_ylim(0, 1500)
    
    for tabaka in tabakalar:
        ax.add_patch(patches.Rectangle((0, 0), tabaka['uzunluk'], tabaka['genislik'], fill=True, color="lightblue"))
    
    for parca, tabaka in yerlesimler:
        ax.add_patch(patches.Rectangle((random.randint(0, int(tabaka['uzunluk'] - parca['uzunluk'])),
                                        random.randint(0, int(tabaka['genislik'] - parca['genislik']))),
                                       parca['uzunluk'], parca['genislik'], fill=True, color="red"))
    
    plt.show()

# Başlangıç popülasyonu oluştur
population = generate_initial_population(parcalar, tabakalar, pop_size=10)

# Genetik algoritmayı çalıştır
best_solution = evolve(population, generations=50, mutation_rate=0.05)

# Atık ve etkinlik hesaplamalarını yapalım
waste = calculate_waste(best_solution)
efficiency = calculate_efficiency(best_solution, tabakalar)
cost = calculate_cost(best_solution)

print(f"Atık Alanı: {waste} birim²")
print(f"Tabakaların Etkinliği: {efficiency:.2f}%")
print(f"Toplam Maliyet: {cost} birim")

# Görselleştirme
visualize_layout(parcalar, tabakalar, best_solution)
