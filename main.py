import random
import math
import csv
import matplotlib.pyplot as plt


# ============================================================
# UNIVERSO DAS FORMIGAS
# V0.2 - REPRODUÇÃO CORRIGIDA
# ============================================================


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

WORLD_SIZE = 100

NUMBER_OF_COLONIES = 3

INITIAL_MALES = 20
INITIAL_FEMALES = 20

# Recursos do arbusto
STARTING_LEAVES = 100.0
STARTING_FRUITS = 50.0

LEAF_REGENERATION = 1.0
FRUIT_REGENERATION = 0.3

# Energia
STARTING_ENERGY = 100.0
BABY_ENERGY = 50.0

LEAF_ENERGY = 12.0
FRUIT_ENERGY = 25.0

# Biologia
MAX_AGE = 1500
MATURITY_AGE = 50

# Movimento
MOVEMENT_SPEED = 1.2

# Reprodução
PREGNANCY_DURATION = 30
REPRODUCTION_COOLDOWN = 40

# Simulação
SIMULATION_DAYS = 1000
REPORT_EVERY = 50


# ============================================================
# 2. FORMIGA
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

        # Posição
        self.x = x
        self.y = y

        # Biologia
        self.sex = sex
        self.age = age
        self.energy = STARTING_ENERGY

        # Organização social
        self.colony = colony
        self.role = role

        # Reprodução
        self.pregnancy = 0
        self.reproduction_cooldown = 0

        # Vida
        self.alive = True

        # Pequena variação individual
        self.strength = random.uniform(
            0.8,
            1.2
        )

    # --------------------------------------------------------
    # MOVIMENTO
    # --------------------------------------------------------

    def move_towards(
        self,
        target_x,
        target_y
    ):

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.hypot(
            dx,
            dy
        )

        if distance == 0:
            return

        self.x += (
            dx / distance
        ) * MOVEMENT_SPEED

        self.y += (
            dy / distance
        ) * MOVEMENT_SPEED

        # Limites do universo
        self.x = max(
            0,
            min(
                WORLD_SIZE,
                self.x
            )
        )

        self.y = max(
            0,
            min(
                WORLD_SIZE,
                self.y
            )
        )

        # Movimento custa energia
        self.energy -= 0.15

    # --------------------------------------------------------
    # PASSAGEM DE UM DIA
    # --------------------------------------------------------

    def live_one_day(self):

        self.age += 1

        # Metabolismo
        self.energy -= 0.1

        # Cooldown
        if self.reproduction_cooldown > 0:

            self.reproduction_cooldown -= 1

        # Gestação
        if self.pregnancy > 0:

            self.pregnancy -= 1

    # --------------------------------------------------------
    # PODE REPRODUZIR?
    # --------------------------------------------------------

    def can_reproduce(self):

        if not self.alive:
            return False

        # Rainha não participa deste sistema
        if self.role == "queen":
            return False

        # Precisa estar madura
        if self.age < MATURITY_AGE:
            return False

        # Energia mínima
        if self.energy < 40:
            return False

        # Precisa estar disponível
        if self.reproduction_cooldown > 0:
            return False

        # Fêmea grávida não pode engravidar novamente
        if (
            self.sex == "F"
            and self.pregnancy > 0
        ):
            return False

        return True


# ============================================================
# 3. COLÔNIA
# ============================================================

class Colony:

    def __init__(
        self,
        name,
        x,
        y
    ):

        self.name = name

        self.x = x
        self.y = y

        self.ants = []

        # Estatísticas
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

        self.ants.append(
            queen
        )

        # Machos
        for _ in range(
            INITIAL_MALES
        ):

            male = Ant(
                self.x,
                self.y,
                "M",
                self,
                age=random.randint(
                    MATURITY_AGE,
                    300
                )
            )

            self.ants.append(
                male
            )

        # Fêmeas
        for _ in range(
            INITIAL_FEMALES
        ):

            female = Ant(
                self.x,
                self.y,
                "F",
                self,
                age=random.randint(
                    MATURITY_AGE,
                    300
                )
            )

            self.ants.append(
                female
            )

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
# 4. ARBUSTO
# ============================================================

class Bush:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        self.leaves = STARTING_LEAVES
        self.fruits = STARTING_FRUITS

    # --------------------------------------------------------
    # REGENERAÇÃO
    # --------------------------------------------------------

    def regenerate(self):

        self.leaves = min(
            STARTING_LEAVES,
            self.leaves
            + LEAF_REGENERATION
        )

        self.fruits = min(
            STARTING_FRUITS,
            self.fruits
            + FRUIT_REGENERATION
        )


# ============================================================
# 5. UNIVERSO
# ============================================================

class World:

    def __init__(self):

        self.day = 0

        # Arbusto central
        self.bush = Bush(
            WORLD_SIZE / 2,
            WORLD_SIZE / 2
        )

        self.colonies = []

        # Estatísticas globais
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

        self.history_births = []
        self.history_deaths = []

        self.history_leaves = []
        self.history_fruits = []

        self.create_colonies()

    # --------------------------------------------------------
    # CRIA TRÊS COLÔNIAS
    # --------------------------------------------------------

    def create_colonies(self):

        center_x = WORLD_SIZE / 2
        center_y = WORLD_SIZE / 2

        # Distância do centro
        radius = 35

        for i in range(
            NUMBER_OF_COLONIES
        ):

            angle = math.radians(
                90 + i * 120
            )

            x = (
                center_x
                + radius
                * math.cos(angle)
            )

            y = (
                center_y
                + radius
                * math.sin(angle)
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
    # DISTÂNCIA AO ARBUSTO
    # --------------------------------------------------------

    def distance_to_bush(
        self,
        ant
    ):

        return math.hypot(
            ant.x - self.bush.x,
            ant.y - self.bush.y
        )

    # --------------------------------------------------------
    # ALIMENTAÇÃO
    # --------------------------------------------------------

    def feed_ant(
        self,
        ant
    ):

        distance = (
            self.distance_to_bush(
                ant
            )
        )

        # Área de alimentação
        if distance < 3:

            # Fruto
            if self.bush.fruits >= 1:

                self.bush.fruits -= 1

                ant.energy += (
                    FRUIT_ENERGY
                )

            # Folha
            elif self.bush.leaves >= 1:

                self.bush.leaves -= 1

                ant.energy += (
                    LEAF_ENERGY
                )

            # Limite
            ant.energy = min(
                ant.energy,
                150
            )

    # --------------------------------------------------------
    # MOVIMENTO
    # --------------------------------------------------------

    def move_ants(self):

        for ant in self.all_ants():

            # Se estiver com pouca energia,
            # procura alimento.
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

            self.feed_ant(
                ant
            )

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
                    and ant.role == "worker"
                    and ant.can_reproduce()
                )
            ]

            random.shuffle(
                males
            )

            for male in males:

                if not females:
                    break

                # Procura a fêmea mais próxima
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

                # Precisam estar próximos
                if distance < 2:

                    # Inicia gestação
                    female.pregnancy = (
                        PREGNANCY_DURATION
                    )

                    # Marca que existe uma
                    # gestação ativa
                    female.was_pregnant = True

                    # Cooldowns
                    male.reproduction_cooldown = (
                        REPRODUCTION_COOLDOWN
                    )

                    female.reproduction_cooldown = (
                        REPRODUCTION_COOLDOWN
                    )

                    # Custo energético
                    male.energy -= 5
                    female.energy -= 10

                    colony.matings += 1
                    self.total_matings += 1

                    # Essa fêmea não pode ser
                    # escolhida novamente neste dia
                    females.remove(
                        female
                    )

    # --------------------------------------------------------
    # GESTAÇÃO E NASCIMENTO
    # --------------------------------------------------------

    def process_pregnancies(self):

        for colony in self.colonies:

            for mother in colony.living_ants():

                if mother.sex != "F":
                    continue

                if mother.role != "worker":
                    continue

                # Se ainda está grávida,
                # não fazemos nada.
                if mother.pregnancy > 0:
                    continue

                # Se a gestação terminou,
                # nasce exatamente um filhote.
                if getattr(
                    mother,
                    "was_pregnant",
                    False
                ):

                    baby_sex = random.choice(
                        ["M", "F"]
                    )

                    baby = Ant(
                        mother.x,
                        mother.y,
                        baby_sex,
                        colony,
                        age=0,
                        role="worker"
                    )

                    baby.energy = (
                        BABY_ENERGY
                    )

                    colony.ants.append(
                        baby
                    )

                    colony.births += 1

                    self.total_births += 1

                    # A gestação foi consumida
                    mother.was_pregnant = False

    # --------------------------------------------------------
    # MORTES
    # --------------------------------------------------------

    def process_deaths(self):

        for colony in self.colonies:

            for ant in colony.living_ants():

                # Ninguém morre se estiver
                # simplesmente grávida.
                if ant.energy <= 0:

                    # A rainha também pode morrer
                    # nesta versão.
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

        self.history_births.append(
            self.total_births
        )

        self.history_deaths.append(
            self.total_deaths
        )

        self.history_leaves.append(
            self.bush.leaves
        )

        self.history_fruits.append(
            self.bush.fruits
        )

    # --------------------------------------------------------
    # UM DIA
    # --------------------------------------------------------

    def step(self):

        self.day += 1

        # 1. Todos envelhecem
        for ant in self.all_ants():

            ant.live_one_day()

        # 2. Movimento e alimentação
        self.move_ants()

        # 3. Acasalamento
        self.reproduce()

        # 4. Gestações e nascimentos
        self.process_pregnancies()

        # 5. Arbusto cresce novamente
        self.bush.regenerate()

        # 6. Mortes
        self.process_deaths()

        # 7. Salvar estado do universo
        self.record_history()

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    def report(self):

        print()
        print("=" * 65)
        print(
            f"DIA {self.day}"
        )
        print("=" * 65)

        for colony in self.colonies:

            ants = colony.living_ants()

            queens = sum(
                ant.role == "queen"
                for ant in ants
            )

            males = sum(
                ant.sex == "M"
                for ant in ants
            )

            females = sum(
                (
                    ant.sex == "F"
                    and ant.role == "worker"
                )
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
                f"Rainhas: {queens} | "
                f"Machos: {males} | "
                f"Fêmeas: {females} | "
                f"Energia média: "
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
            f"Total → "
            f"nascimentos: "
            f"{self.total_births} | "
            f"mortes: "
            f"{self.total_deaths} | "
            f"acasalamentos: "
            f"{self.total_matings}"
        )


# ============================================================
# GRÁFICO DE POPULAÇÃO
# ============================================================

def create_population_graph(
    world
):

    plt.figure(
        figsize=(10, 6)
    )

    for colony in world.colonies:

        plt.plot(
            world.history_days,
            world.history_population[
                colony.name
            ],
            label=(
                f"Colônia "
                f"{colony.name}"
            )
        )

    plt.xlabel(
        "Dias"
    )

    plt.ylabel(
        "Número de formigas"
    )

    plt.title(
        "Evolução das populações"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        "populacao.png",
        dpi=150
    )

    plt.close()


# ============================================================
# GRÁFICO DE RECURSOS
# ============================================================

def create_resource_graph(
    world
):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        world.history_days,
        world.history_leaves,
        label="Folhas"
    )

    plt.plot(
        world.history_days,
        world.history_fruits,
        label="Frutos"
    )

    plt.xlabel(
        "Dias"
    )

    plt.ylabel(
        "Quantidade"
    )

    plt.title(
        "Recursos do arbusto"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        "recursos.png",
        dpi=150
    )

    plt.close()


# ============================================================
# SALVA OS DADOS
# ============================================================

def save_data(
    world
):

    with open(
        "historico.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow([
            "dia",
            "colonia_A",
            "colonia_B",
            "colonia_C",
            "nascimentos",
            "mortes",
            "folhas",
            "frutos"
        ])

        for i in range(
            len(world.history_days)
        ):

            writer.writerow([
                world.history_days[i],
                world.history_population["A"][i],
                world.history_population["B"][i],
                world.history_population["C"][i],
                world.history_births[i],
                world.history_deaths[i],
                world.history_leaves[i],
                world.history_fruits[i]
            ])


# ============================================================
# EXECUÇÃO
# ============================================================

world = World()

print()
print("=" * 65)
print("UNIVERSO DAS FORMIGAS - V0.2")
print("=" * 65)

print(
    "Reprodução corrigida."
)

print(
    "Gestação: "
    f"{PREGNANCY_DURATION} dias."
)

print(
    "Cada gestação gera "
    "exatamente 1 filhote."
)

print(
    f"População inicial: "
    f"{len(world.all_ants())}"
)

print(
    f"Simulação: "
    f"{SIMULATION_DAYS} dias."
)

print()


# ============================================================
# SIMULAÇÃO
# ============================================================

for _ in range(
    SIMULATION_DAYS
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

create_population_graph(
    world
)

create_resource_graph(
    world
)

save_data(
    world
)


# ============================================================
# RELATÓRIO FINAL
# ============================================================

print()
print("=" * 65)
print("SIMULAÇÃO FINALIZADA")
print("=" * 65)

world.report()

print()
print("Arquivos criados:")

print(
    "  populacao.png"
)

print(
    "  recursos.png"
)

print(
    "  historico.csv"
)

print()
print(
    "V0.2 concluída."
)