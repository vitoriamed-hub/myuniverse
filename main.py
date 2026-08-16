import random
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_agg import FigureCanvasAgg


# ============================================================
# CONFIGURAÇÕES DO UNIVERSO - V0.2
# ============================================================

WORLD_SIZE = 100

INITIAL_MALES = 20
INITIAL_FEMALES = 20

# Recursos iniciais
STARTING_LEAVES = 100
STARTING_FRUITS = 50

# Regeneração
LEAF_REGENERATION = 1.0
FRUIT_REGENERATION = 0.3

# Energia
STARTING_ENERGY = 100
BABY_ENERGY = 50

LEAF_ENERGY = 12
FRUIT_ENERGY = 25

# Biologia
MAX_AGE = 1500
MATURITY_AGE = 50

# Movimento
MOVEMENT_SPEED = 1.2

# Reprodução
PREGNANCY_DURATION = 30
REPRODUCTION_COOLDOWN = 40

# Simulação
SIMULATION_STEPS = 1000
REPORT_EVERY = 50


# ============================================================
# FORMIGA
# ============================================================

class Ant:

    next_id = 0

    def __init__(
        self,
        x,
        y,
        sex,
        colony,
        age=0,
        role="worker"
    ):

        self.id = Ant.next_id
        Ant.next_id += 1

        self.x = x
        self.y = y

        self.sex = sex
        self.colony = colony
        self.role = role

        self.age = age

        self.energy = STARTING_ENERGY

        # Pequenas diferenças individuais
        self.strength = random.uniform(0.8, 1.2)

        # Reprodução
        self.pregnancy = 0
        self.reproduction_cooldown = 0

        self.alive = True

    # --------------------------------------------------------
    # MOVIMENTO
    # --------------------------------------------------------

    def move_towards(self, target_x, target_y):

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.hypot(dx, dy)

        if distance == 0:
            return

        self.x += (
            dx / distance
        ) * MOVEMENT_SPEED

        self.y += (
            dy / distance
        ) * MOVEMENT_SPEED

        self.x = max(
            0,
            min(WORLD_SIZE, self.x)
        )

        self.y = max(
            0,
            min(WORLD_SIZE, self.y)
        )

        self.energy -= 0.15

    # --------------------------------------------------------
    # ENVELHECIMENTO
    # --------------------------------------------------------

    def age_one_day(self):

        self.age += 1

        self.energy -= 0.1

        if self.reproduction_cooldown > 0:

            self.reproduction_cooldown -= 1

        if self.pregnancy > 0:

            self.pregnancy -= 1

    # --------------------------------------------------------
    # PODE REPRODUZIR?
    # --------------------------------------------------------

    def can_reproduce(self):

        if not self.alive:
            return False

        if self.role == "queen":
            return False

        if self.age < MATURITY_AGE:
            return False

        if self.energy < 40:
            return False

        if self.reproduction_cooldown > 0:
            return False

        if self.sex == "F" and self.pregnancy > 0:
            return False

        return True


# ============================================================
# COLÔNIA
# ============================================================

class Colony:

    def __init__(self, name, x, y):

        self.name = name

        self.x = x
        self.y = y

        self.ants = []

        self.births = 0
        self.deaths = 0
        self.matings = 0

        self.create_initial_population()

    # --------------------------------------------------------
    # POPULAÇÃO INICIAL
    # --------------------------------------------------------

    def create_initial_population(self):

        # Rainha
        queen = Ant(
            self.x,
            self.y,
            "F",
            self,
            age=300,
            role="queen"
        )

        self.ants.append(queen)

        # Machos
        for _ in range(INITIAL_MALES):

            male = Ant(
                self.x,
                self.y,
                "M",
                self,
                age=random.randint(50, 300)
            )

            self.ants.append(male)

        # Fêmeas
        for _ in range(INITIAL_FEMALES):

            female = Ant(
                self.x,
                self.y,
                "F",
                self,
                age=random.randint(50, 300)
            )

            self.ants.append(female)

    # --------------------------------------------------------
    # FORMIGAS VIVAS
    # --------------------------------------------------------

    def living_ants(self):

        return [
            ant
            for ant in self.ants
            if ant.alive
        ]

    # --------------------------------------------------------
    # POPULAÇÃO
    # --------------------------------------------------------

    def population(self):

        return len(
            self.living_ants()
        )


# ============================================================
# ARBUSTO
# ============================================================

class Bush:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.leaves = STARTING_LEAVES
        self.fruits = STARTING_FRUITS

    def regenerate(self):

        self.leaves = min(
            STARTING_LEAVES,
            self.leaves + LEAF_REGENERATION
        )

        self.fruits = min(
            STARTING_FRUITS,
            self.fruits + FRUIT_REGENERATION
        )


# ============================================================
# UNIVERSO
# ============================================================

class World:

    def __init__(self):

        self.day = 0

        self.colonies = []

        self.bush = Bush(
            WORLD_SIZE / 2,
            WORLD_SIZE / 2
        )

        self.total_births = 0
        self.total_deaths = 0
        self.total_matings = 0

        # Histórico
        self.history_days = []

        self.history_population = {
            "A": [],
            "B": [],
            "C": []
        }

        self.history_food = []

        self.create_colonies()

    # --------------------------------------------------------
    # CRIA AS COLÔNIAS
    # --------------------------------------------------------

    def create_colonies(self):

        center_x = WORLD_SIZE / 2
        center_y = WORLD_SIZE / 2

        radius = 35

        for i in range(3):

            angle = math.radians(
                90 + i * 120
            )

            x = (
                center_x
                + radius * math.cos(angle)
            )

            y = (
                center_y
                + radius * math.sin(angle)
            )

            colony = Colony(
                chr(65 + i),
                x,
                y
            )

            self.colonies.append(
                colony
            )

    # --------------------------------------------------------
    # TODAS AS FORMIGAS
    # --------------------------------------------------------

    def all_ants(self):

        ants = []

        for colony in self.colonies:

            ants.extend(
                colony.living_ants()
            )

        return ants

    # --------------------------------------------------------
    # DISTÂNCIA ATÉ O ARBUSTO
    # --------------------------------------------------------

    def distance_to_bush(self, ant):

        return math.hypot(
            ant.x - self.bush.x,
            ant.y - self.bush.y
        )

    # --------------------------------------------------------
    # ALIMENTAÇÃO
    # --------------------------------------------------------

    def feed_ant(self, ant):

        if (
            self.distance_to_bush(ant)
            < 3
        ):

            if self.bush.fruits >= 1:

                self.bush.fruits -= 1

                ant.energy += FRUIT_ENERGY

            elif self.bush.leaves >= 1:

                self.bush.leaves -= 1

                ant.energy += LEAF_ENERGY

            ant.energy = min(
                ant.energy,
                150
            )

    # --------------------------------------------------------
    # MOVIMENTO
    # --------------------------------------------------------

    def move_ants(self):

        for ant in self.all_ants():

            # Pouca energia → procurar comida
            if ant.energy < 70:

                ant.move_towards(
                    self.bush.x,
                    self.bush.y
                )

            else:

                # Exploração aleatória
                angle = random.uniform(
                    0,
                    2 * math.pi
                )

                target_x = (
                    ant.x
                    + math.cos(angle) * 5
                )

                target_y = (
                    ant.y
                    + math.sin(angle) * 5
                )

                ant.move_towards(
                    target_x,
                    target_y
                )

            self.feed_ant(ant)

    # --------------------------------------------------------
    # REPRODUÇÃO
    # --------------------------------------------------------

    def reproduce(self):

        for colony in self.colonies:

            males = [
                ant
                for ant in colony.living_ants()
                if (
                    ant.sex == "M"
                    and ant.can_reproduce()
                )
            ]

            females = [
                ant
                for ant in colony.living_ants()
                if (
                    ant.sex == "F"
                    and ant.role != "queen"
                    and ant.can_reproduce()
                )
            ]

            random.shuffle(males)

            for male in males:

                if not females:
                    break

                female = min(
                    females,
                    key=lambda f:
                    math.hypot(
                        male.x - f.x,
                        male.y - f.y
                    )
                )

                distance = math.hypot(
                    male.x - female.x,
                    male.y - female.y
                )

                if distance < 2:

                    # Começa a gestação
                    female.pregnancy = (
                        PREGNANCY_DURATION
                    )

                    male.reproduction_cooldown = (
                        REPRODUCTION_COOLDOWN
                    )

                    female.reproduction_cooldown = (
                        REPRODUCTION_COOLDOWN
                    )

                    male.energy -= 5
                    female.energy -= 10

                    colony.matings += 1
                    self.total_matings += 1

                    females.remove(
                        female
                    )

    # --------------------------------------------------------
    # GESTAÇÃO
    # --------------------------------------------------------

    def process_pregnancies(self):

        for colony in self.colonies:

            for mother in colony.living_ants():

                if mother.sex != "F":
                    continue

                if mother.role == "queen":
                    continue

                # A gestação acabou
                if (
                    mother.pregnancy == 0
                    and getattr(
                        mother,
                        "was_pregnant",
                        False
                    )
                ):

                    # Nasce exatamente UM filhote
                    sex = random.choice(
                        ["M", "F"]
                    )

                    baby = Ant(
                        mother.x,
                        mother.y,
                        sex,
                        colony,
                        age=0
                    )

                    baby.energy = BABY_ENERGY

                    colony.ants.append(
                        baby
                    )

                    colony.births += 1

                    self.total_births += 1

                    mother.was_pregnant = False

                elif mother.pregnancy > 0:

                    mother.was_pregnant = True

    # --------------------------------------------------------
    # MORTE
    # --------------------------------------------------------

    def process_deaths(self):

        for colony in self.colonies:

            for ant in colony.living_ants():

                if ant.energy <= 0:

                    ant.alive = False

                    colony.deaths += 1

                    self.total_deaths += 1

                elif ant.age >= MAX_AGE:

                    ant.alive = False

                    colony.deaths += 1

                    self.total_deaths += 1

    # --------------------------------------------------------
    # REGISTRA HISTÓRICO
    # --------------------------------------------------------

    def record_history(self):

        self.history_days.append(
            self.day
        )

        for colony in self.colonies:

            self.history_population[
                colony.name
            ].append(
                colony.population()
            )

        total_food = (
            self.bush.leaves
            + self.bush.fruits
        )

        self.history_food.append(
            total_food
        )

    # --------------------------------------------------------
    # UM DIA
    # --------------------------------------------------------

    def step(self):

        self.day += 1

        # 1. Envelhecimento
        for ant in self.all_ants():

            ant.age_one_day()

        # 2. Movimento
        self.move_ants()

        # 3. Reprodução
        self.reproduce()

        # 4. Gestação
        self.process_pregnancies()

        # 5. Regeneração
        self.bush.regenerate()

        # 6. Mortes
        self.process_deaths()

        # 7. Histórico
        self.record_history()

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    def report(self):

        print()
        print("=" * 60)
        print(
            f"DIA {self.day}"
        )
        print("=" * 60)

        for colony in self.colonies:

            ants = colony.living_ants()

            males = sum(
                ant.sex == "M"
                for ant in ants
            )

            females = sum(
                ant.sex == "F"
                for ant in ants
                if ant.role != "queen"
            )

            queen = sum(
                ant.role == "queen"
                for ant in ants
            )

            if ants:

                average_energy = (
                    sum(
                        ant.energy
                        for ant in ants
                    )
                    / len(ants)
                )

            else:

                average_energy = 0

            print(
                f"Colônia {colony.name}: "
                f"{len(ants)} formigas | "
                f"👑 {queen} rainha | "
                f"♂ {males} | "
                f"♀ {females} | "
                f"energia média: "
                f"{average_energy:.1f}"
            )

        print(
            f"Recursos → "
            f"folhas: "
            f"{self.bush.leaves:.1f} | "
            f"frutos: "
            f"{self.bush.fruits:.1f}"
        )

        print(
            f"Eventos → "
            f"nascimentos: "
            f"{self.total_births} | "
            f"mortes: "
            f"{self.total_deaths} | "
            f"acasalamentos: "
            f"{self.total_matings}"
        )


# ============================================================
# GRÁFICO FINAL
# ============================================================

def create_final_graph(world):

    plt.figure(
        figsize=(10, 6)
    )

    for colony in world.colonies:

        plt.plot(
            world.history_days,
            world.history_population[
                colony.name
            ],
            label=f"Colônia {colony.name}"
        )

    plt.xlabel(
        "Dias"
    )

    plt.ylabel(
        "População"
    )

    plt.title(
        "Evolução das populações"
    )

    plt.legend()

    plt.grid()

    plt.savefig(
        "populacao.png",
        dpi=150
    )

    plt.close()


# ============================================================
# EXECUÇÃO
# ============================================================

world = World()

print()
print("=" * 60)
print("UNIVERSO DAS FORMIGAS - V0.2")
print("=" * 60)

print(
    f"População inicial: "
    f"{len(world.all_ants())}"
)

print(
    f"Simulação: "
    f"{SIMULATION_STEPS} dias"
)

print()

for day in range(
    SIMULATION_STEPS
):

    world.step()

    if (
        world.day
        % REPORT_EVERY
        == 0
    ):

        world.report()


# ============================================================
# RESULTADOS
# ============================================================

create_final_graph(
    world
)

print()
print("=" * 60)
print("SIMULAÇÃO FINALIZADA")
print("=" * 60)

world.report()

print()
print(
    "Arquivo criado:"
)

print(
    "populacao.png"
)