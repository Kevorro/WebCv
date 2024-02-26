import math
import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Window(QMainWindow):
    # Here we will have the cities like [[10,20],[x,y]....] and this array will not be modified so from here we will know the order of the cities
    cities = []
    # Here we will have our population which is a array of array which includes a sequence meaning the order of the cities above
    population = []
    # Here we have the distances of the population above
    distances = []
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("TSP")
        self.setFixedSize(1500, 950)
        # Set percentages of mutation and crossover
        self.crossover_probability = 0.7
        self.mutation_probability = 0.3
        self.num_of_iterations = 2000
        # We initialize the UI
        self.initUI()

    def initUI(self):
        widget = QWidget()  # Create a widget to contain the layout
        menu_layout = QHBoxLayout()  # Create a horizontal layout
        overview_layout = QHBoxLayout()
        drawingLayout = QHBoxLayout() # Create layout for routes
        main_layout = QVBoxLayout()  # Create a vertical layout

        # Create input fields and button
        self.num_cities_input = QLineEdit()
        self.num_population_input = QLineEdit()
        self.start_city_input = QLineEdit()
        self.num_new_population_input = QLineEdit()
        self.btn_start = QPushButton("Start Algorithm")

        # Add input fields and button to layout
        menu_layout.addWidget(QLabel("Number of cities:"))
        menu_layout.addWidget(self.num_cities_input)
        menu_layout.addWidget(QLabel("Number of Population:"))
        menu_layout.addWidget(self.num_population_input)
        menu_layout.addWidget(QLabel("City to begin with:"))
        menu_layout.addWidget(self.start_city_input)
        menu_layout.addWidget(QLabel("Number of new population generated:"))
        menu_layout.addWidget(self.num_new_population_input)
        menu_layout.addWidget(self.btn_start)

        # Initialize the Drawing of cities
        self.fisrt_route = Drawing()
        self.city_drawing = Drawing()
        self.city_drawing.resize(400, 900)

        # Set the components to the main layout
        main_layout.addLayout(menu_layout)
        drawingLayout.addWidget(self.fisrt_route)
        drawingLayout.addWidget(self.city_drawing)
        main_layout.addLayout(drawingLayout,stretch=8)

        #Tha data that will display
        self.label_first_route = QLabel()
        self.label_best_route = QLabel()

        self.label_first_route.setFont(QFont('Arial',8))
        self.label_best_route.setFont(QFont('Arial', 8))

        self.label_first_route.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label_best_route.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.label_first_route.setWordWrap(True)
        self.label_best_route.setWordWrap(True)

        self.label_first_route.setStyleSheet("background:#424242; color:#fff")
        self.label_best_route.setStyleSheet("background:#424242; color:#fff")

        #Add the label were data will be viewed
        overview_layout.addWidget(self.label_first_route)
        overview_layout.addWidget(self.label_best_route)
        main_layout.addLayout(overview_layout,stretch=1)

        widget.setLayout(main_layout)  # Set the layout for the widget
        self.setCentralWidget(widget)  # Set the widget as the central widget

        # Connect button click event to start algorithm function
        self.btn_start.clicked.connect(self.startAlgorithm)

    def startAlgorithm(self):
        # Get input values from the user
        self.num_cities = int(self.num_cities_input.text())
        self.num_population = int(self.num_population_input.text())
        self.start_city = int(self.start_city_input.text())
        self.num_new_population = int(self.num_new_population_input.text())

        # We set up how much population of the new population will be by crossover and mutation
        new_population_by_crossover = math.ceil(self.num_new_population * self.crossover_probability)
        new_population_by_mutation = self.num_new_population - new_population_by_crossover

        self.initializeCities()# Initialize the coordenates of the cities
        self.initializePopulation()# Initialize the population that has the different paths

        self.fisrt_route.getPoints(self.cities,self.start_city) #We introduce the cities to the first best route
        self.city_drawing.getPoints(self.cities,self.start_city) #We introduce the same cities but this one will be changing

        best_distance = float('inf')
        cont = 0
        while cont < self.num_of_iterations:
            for c in range(new_population_by_crossover):
                self.croossover()  # We start creating new population based on crossover
            for m in range(new_population_by_mutation):
                self.mutation()  # we start to create new population based on mutation
            if self.distances:
                self.distances.clear()  # weclear the distances through each new iteration
            self.calculateRoutes()
            for ni in range(self.num_new_population):
                self.removeBigRoutes()

            current_best_route = min(self.distances)

            if cont == 0:
                first_route = self.population[self.distances.index(min(self.distances))]
                first_distance = min(self.distances)
                self.fisrt_route.getBestRoute(first_route)
                self.fisrt_route.repaint()
                first_route_text = f"<b>Overview</b><br>Best distance: {first_distance}<br>Route taken: {first_route}"
                self.label_first_route.setText(first_route_text)
            elif current_best_route < best_distance:
                best_distance = current_best_route
                best_route = self.population[self.distances.index(best_distance)]
                self.city_drawing.getBestRoute(best_route)
                #self.num_of_iterations += 200
                self.city_drawing.repaint()
                best_route_text = f"<b>Overview</b><br>Best distance: {best_distance}<br>Route taken: {best_route} <br>Reduced distance: {first_distance-best_distance}"
                self.label_best_route.setText(best_route_text)
                QThread.msleep(500)
                if cont % 200 == 0:
                    self.num_of_iterations += 200

            print(cont)
            cont+=1



    def initializeCities(self):
        # We get the height and width of the drawing
        height = self.city_drawing.height()
        width = self.city_drawing.width()
        city_position = []
        for i in range(self.num_cities):
            x = random.randint(1, width - 1)
            city_position.append(x)
            y = random.randint(1, height - 1)
            city_position.append(y)
            self.cities.append(city_position.copy())
            city_position.clear()

    def initializePopulation(self):
        for _ in range(self.num_population):
            individual = list(range(1, self.num_cities+1))  # Create a new individual
            individual.remove(self.start_city)  # Remove the start city from the individual
            random.shuffle(individual)  # Shuffle the remaining cities
            individual.insert(0, self.start_city)  # Insert the start city at the beginning of the individual
            self.population.append(individual)  # Append the individual to the population

    def fitness(self,individual): #Here we get the distance between each point its just the formula to get a distance beetween 2 points
        distance = 0
        for i in range(self.num_cities - 1):
            x1, y1 = self.cities[individual[i]-1]
            x2, y2 = self.cities[individual[i+1]-1]
            distance += math.sqrt((x2-x1)**2 + (y2-y1)**2)
        x1, y1 = self.cities[individual[self.num_cities -1] - 1]
        x2, y2 = self.cities[individual[0] - 1]
        distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

    def getRoutes(self): #Here we calculate from the population the distance it made following each city
        for i in range(self.num_population-1):
            total_distance = self.fitness(self.population[i])
            self.distances.append(total_distance)

    def croossover(self): #Here we will do the crossover to generate new population of posible routes
        randomIndex1, randomIndex2 = random.sample(range(self.num_population), 2)  # Randomly select two indices without repetition
        aux = [self.population[randomIndex1][:], self.population[randomIndex2][:]]  # Create shallow copies of the sublists in aux
        new_indivudual = [aux[0][0]]  # Create a new list for the new population
        del aux[0][0], aux[1][0]  # Remove the first element from both sublists in aux
        a2 = 0  # Initialize a2
        new_indivudual.append(aux[0][a2])  # Append the first element from the second sublist in aux to np
        while not self.insideOfNewInidividual(aux[1][a2],new_indivudual):  # While the current number from the second sublist in aux is not in new_indivudual
            numOfCity = aux[1][a2]  # Store the current number from the second sublist in aux in the variable NumOfCity
            new_indivudual.append(numOfCity)  # Append numOfCity to new_indivudual
            a2 = aux[0].index(numOfCity)  # Update a2 to the index of new_indivudual in the first sublist in aux
        for v in range(len(new_indivudual) - 1):  #Remove the elements from new_indivudual that we've already added from the second sublist in aux
            aux[1].remove(new_indivudual[v + 1])
        new_indivudual.extend(aux[1])  # Extend np with the remaining elements from the second sublist in aux
        self.population.append(new_indivudual.copy())  # Add the new population to the population list
        new_indivudual.clear()

    def insideOfNewInidividual(self, a2, newI):
        return a2 in newI

    def mutation(self):
        newIndividual = self.population[random.randint(0, self.num_population - 1)].copy() # Select a random individual from the population
        p1, p2 = random.sample(range(2, self.num_cities), 2)  #Select two unique random positions in the chromosome
        newIndividual[p1-1], newIndividual[p2-1] = newIndividual[p2-1], newIndividual[p1-1]  # Swap the cities at positions p1 and p2
        self.population.append(newIndividual)# Add the mutated individual back to the population

    def calculateRoutes(self):
        for route in self.population:
            dist = self.fitness(route)
            self.distances.append(dist)

    def removeBigRoutes(self): # Check if the distances list is not empty
        max_distance_index = self.distances.index(max(self.distances))  # Find the index of the maximum distance
        self.population.pop(max_distance_index)  # Remove the corresponding route from the population list
        self.distances.pop(max_distance_index)  # Remove the maximum distance from the distances list
class Drawing(QWidget):
    cities = []
    bestRoute = []
    start_city = 0
    def paintEvent(self, event):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.yellow)
        self.setPalette(palette)
        painter = QPainter(self)
        if (bool(self.cities)):
            for idx, city in enumerate(self.cities,start=1):
                x,y = city
                if self.cities[self.start_city -1] == city:
                    pen = QPen(QColor(Qt.blue))
                    pen.setWidth(4)
                    painter.setPen(pen)
                else:
                    pen = QPen(Qt.black)
                    pen.setWidth(4)
                    painter.setPen(pen)
                painter.drawPoint(x, y)
                painter.drawText(x,y-5,str(idx))
        if bool(self.bestRoute):
            for i in range(len(self.bestRoute) - 1):
                x1, y1 = self.cities[self.bestRoute[i]-1]
                x2, y2 = self.cities[self.bestRoute[i+1]-1]
                if i == 0:
                    pen = QPen(QColor(Qt.blue))
                    pen.setWidth(1)
                    painter.setPen(pen)
                else:
                    pen = QPen(Qt.black)
                    pen.setWidth(1)
                    painter.setPen(pen)
                painter.drawLine(x1, y1, x2, y2)
            # Draw the line connecting the last city to the first city
            x1, y1 = self.cities[self.bestRoute[-1] - 1]
            x2, y2 = self.cities[self.bestRoute[0] - 1]
            painter.drawLine(x1, y1, x2, y2)
    def getPoints(self, points,starC):
        self.cities = points
        self.start_city = starC
        self.update()
    def getBestRoute(self, bRoute):
        self.bestRoute = bRoute
        self.update();

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit_code = app.exec_()
    return sys.exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)