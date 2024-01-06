import copy
from itertools import permutations, combinations
from math import factorial


# Class definition for Seller
class Seller:
    def __init__(self, name, resources):
        # Initialize Seller with a name and available resources
        self.name = name
        self.resources = resources
        self.coalitions = []  # List to store the coalitions the seller is part of
        self.revenue = 0

    def join_coalition(self, coalition):
        # Method for a seller to join a coalition
        self.coalitions.append(coalition)

    def clear_coalition(self):
        # Method to clear the list of coalitions for a seller
        self.coalitions.clear()

    def prioritize_coalitions(self):
        # Method to prioritize coalitions based on revenue
        self.coalitions.sort(key=lambda coalition: coalition.sort_based_revenue(self, coalition.buyer.amount_to_pay),
                             reverse=True)

    def __repr__(self):
        return f"Seller({self.name}, {self.resources})"

    def __eq__(self, other):
        # Define equality for sellers based on their names
        return isinstance(other, Seller) and other.name == self.name

    def __hash__(self):
        # Define a hash function for sellers based on their names
        return self.name.__hash__()


# Class definition for Buyer
class Buyer:
    def __init__(self, name, demand, amount_to_pay):
        # Initialize Buyer with a name, demand, and amount to pay
        self.name = name
        self.demand = demand
        self.amount_to_pay = amount_to_pay

    def __repr__(self):
        return f"Buyer({self.name}, {self.demand}, {self.amount_to_pay})"

    def __eq__(self, other):
        # Define equality for buyers based on their names
        return isinstance(other, Buyer) and other.name == self.name

    def __hash__(self):
        # Define a hash function for buyers based on their names
        return self.name.__hash__()


# Class definition for Coalition
class Coalition:
    def __init__(self, buyer, shapley_value, sellers=None):
        # Initialize Coalition with a buyer, Shapley value, and optional sellers
        self.buyer = buyer
        self.sellers = sellers if sellers else []
        self.shapley_value = shapley_value

    def add_seller(self, seller: Seller):
        # Method to add a seller to the coalition
        if seller.name not in [s.name for s in self.sellers]:
            self.sellers.append(seller)
            seller.join_coalition(self)

    def total_resources(self):
        # Calculate the total resources of the coalition
        return sum(seller.resources for seller in self.sellers)

    def is_sufficient(self):
        # Check if the coalition has sufficient resources to meet the buyer's demand
        return self.total_resources() == self.buyer.demand

    def sort_based_revenue(self, seller, pay_amount):
        # Calculate the revenue for a seller within the coalition
        if seller.name not in [s.name for s in self.sellers]:
            return 0

        shapley_values = {s: self.shapley_value[s.name] for s in self.sellers}
        sum_of_shapley = sum(shapley_values.values())

        return (shapley_values[seller] / sum_of_shapley) * pay_amount

    def get_avg_rank(self, temp_sellers):
        # Calculate the average rank of the coalition among sellers
        relevant_sellers = [seller for seller in temp_sellers if self in seller.coalitions]

        if not relevant_sellers:
            return 0

        total_rank = sum(seller.coalitions.index(self) for seller in relevant_sellers)
        return total_rank / len(relevant_sellers)

    def __repr__(self):
        return f"Coalition({self.buyer}, {self.sellers})"


# Class definition for CG-TTC algorithm
class CgTtc:
    """
    CgTtc class represents the implementation of the Cooperative Game - Top Trading Cycle (CG-TTC) algorithm.
    CG-TTC is an algorithm used for resource allocation in cooperative games, where a set of sellers and buyers
    interact to form coalitions and trade resources.

    The algorithm consists of several methods for calculating Shapley values, generating sufficient coalitions,
    executing one round of the algorithm, evaluating the performance, and more.

    Attributes:
        all_shapley_values (dict): A dictionary to store calculated Shapley values for different value lists.

    Methods:
        calculate_shapley_value: Calculates Shapley values for players using a given coalition value function.
        coalition_value_function: Defines a coalition value function as the sum of values for players in the coalition.
        generate_sufficient_coalitions: Generates all sufficient coalitions for a given set of sellers and a buyer.
        one_round: Executes one round of the CG-TTC algorithm.
        ideal_profit: Calculates the ideal profit given the available resources and a list of buyers.
        gini_coefficient: Calculates the Gini coefficient for a given list of numbers.
        cg_ttc_run: Runs the CG-TTC algorithm.
        eval_fun: Evaluates the performance of the CG-TTC algorithm and writes results to a file.
    """
    
    def __init__(self):
        self.all_shapley_values = {}  # Dictionary to store calculated Shapley values

    def calculate_shapley_value(self, players, val_list, coalition_value_function):
        """
        Calculates Shapley values for players using a given coalition value function.

        Args:
            players (list): List of players.
            val_list (dict): Dictionary of values for each player.
            coalition_value_function (function): Coalition value function.

        Returns:
            dict: Dictionary of Shapley values for each player.
        """
        val_str = val_list.__str__()
        if val_str in self.all_shapley_values:
            return self.all_shapley_values[val_str]

        num_players = len(players)
        shapley_values = {}

        for player in players:
            shapley_value = 0

            for coalition_size in range(1, num_players + 1):
                for coalition in permutations(players, coalition_size):
                    if player in coalition:
                        without_player = tuple(p for p in coalition if p != player)
                        marginal_contribution = coalition_value_function(coalition,
                                                                         val_list) - coalition_value_function(
                            without_player, val_list)
                        shapley_value += marginal_contribution / (
                                factorial(coalition_size - 1) * factorial(num_players - coalition_size))

            shapley_values[player] = shapley_value

        self.all_shapley_values[val_str] = shapley_values
        return shapley_values

    @staticmethod
    def coalition_value_function(coalition, val_list):
        """
        Defines a coalition value function as the sum of values for players in the coalition.

        Args:
            coalition (list): List of players in the coalition.
            val_list (dict): Dictionary of values for each player.

        Returns:
            int: Coalition value.
        """
        return sum(val_list[player] for player in coalition)

    def generate_sufficient_coalitions(self, sellers, buyer):
        """
        Generates all sufficient coalitions for a given set of sellers and a buyer.

        Args:
            sellers (list): List of sellers.
            buyer (Buyer): Buyer object.

        Returns:
            list: List of sufficient coalitions.
        """
        temp_coalitions = []

        for r in range(1, len(sellers) + 1):
            for subset in combinations(sellers, r):
                players = [seller.name for seller in subset]
                values = {seller.name: seller.resources for seller in subset}

                if any(values[name] <= 0 for name in players):
                    continue

                shapley_value = self.calculate_shapley_value(players, values, self.coalition_value_function)

                if any(value <= 0 for value in shapley_value.values()):
                    continue

                s = sum(shapley_value.values())
                share = {subset[index].name: round((i * buyer.demand) / s) for index, i in
                         enumerate(shapley_value.values())}

                if any(share[name] > subset[index].resources or share[name] <= 0 for index, name in
                       enumerate(shapley_value.keys())):
                    continue

                new_set = [Seller(name, share[name]) for name in share]
                coalition = Coalition(buyer, shapley_value, new_set)

                if coalition.is_sufficient():
                    temp_coalitions.append(coalition)

        return temp_coalitions

    def one_round(self, sellers, buyers):
        """
        Executes one round of the CG-TTC algorithm.

        Args:
            sellers (list): List of sellers.
            buyers (list): List of buyers.

        Returns:
            list: Updated list of sellers.
        """
        for seller in sellers:
            seller.clear_coalition()

        all_coalitions = []
        for buyer in buyers:
            temp_all_coalitions = self.generate_sufficient_coalitions(sellers, buyer)
            all_coalitions.extend(temp_all_coalitions)

        # Sellers join all possible Coalitions
        for seller in sellers:
            for coalition in all_coalitions:
                if seller.name in [s.name for s in coalition.sellers]:
                    for s in coalition.sellers:
                        if s.resources != 0:
                            seller.join_coalition(coalition)
                            break

        # Sellers prioritize their Coalitions
        for seller in sellers:
            seller.prioritize_coalitions()

        return sellers

    @staticmethod
    def ideal_profit(resources: int, buyers: list):
        """
        Calculates the ideal profit given the available resources and a list of buyers.

        Args:
            resources (int): Available resources.
            buyers (list): List of buyers.

        Returns:
            int: Ideal profit.
        """
        sorted_buyers = sorted(buyers, key=lambda x: x.amount_to_pay, reverse=True)
        profit = 0

        for buyer in sorted_buyers:
            quantity_sold = min(resources, buyer.demand)
            profit += quantity_sold * buyer.amount_to_pay
            resources -= quantity_sold

            if resources <= 0:
                break

        return profit

    @staticmethod
    def gini_coefficient(numbers: list):
        """
        Calculates the Gini coefficient for a given list of numbers.

        Args:
            numbers (list): List of numbers.

        Returns:
            float: Gini coefficient.
        """
        n = len(numbers)
        mean_value = sum(numbers) / n
        numerator = sum(abs(i - j) for i in numbers for j in numbers)
        denominator = 2 * (n ** 2) * mean_value

        return numerator / denominator if denominator != 0 else 0

    def cg_ttc_run(self, sellers, buyers):
        """
        Runs the CG-TTC algorithm.

        Args:
            sellers (list): List of sellers.
            buyers (list): List of buyers.

        Returns:
            tuple: Tuple containing the list of coalitions, updated list of sellers, and updated list of buyers.
        """
        temp_coalitions = []
        temp_buyers = copy.deepcopy(buyers)
        temp_sellers = copy.deepcopy(sellers)
        deleted_sellers = []

        while len(temp_buyers) > 0:
            temp_sellers1 = self.one_round(temp_sellers, temp_buyers)
            temp_cor = [ss for seller in temp_sellers if seller.coalitions for ss in seller.coalitions]

            if len(temp_cor) == 0:
                temp_sellers.extend(deleted_sellers)
                deleted_sellers = []
                temp_sellers1 = self.one_round(temp_sellers, temp_buyers)
                temp_cor = [ss for seller in temp_sellers if seller.coalitions for ss in seller.coalitions]
            temp_sellers = temp_sellers1

            temp_cor.sort(key=lambda coalition: coalition.get_avg_rank(temp_sellers))
            if not temp_cor:
                break

            top_cor = temp_cor[0]
            temp_buyers.remove(top_cor.buyer)

            for s in top_cor.sellers:
                temp_sellers[temp_sellers.index(s)].resources -= s.resources
                deleted_sellers.append(temp_sellers[temp_sellers.index(s)])
                temp_sellers.remove(s)

            print(top_cor)
            temp_coalitions.append(top_cor)

        temp_sellers.extend(deleted_sellers)
        return temp_coalitions, temp_sellers, temp_buyers

    def eval_fun(self, sellers, buyers, coalitions, temp_sellers, temp_buyers, name):
        """
        Evaluates the performance of the CG-TTC algorithm and writes results to a file.

        Args:
            sellers (list): List of sellers.
            buyers (list): List of buyers.
            coalitions (list): List of coalitions.
            temp_sellers (list): Updated list of sellers.
            temp_buyers (list): Updated list of buyers.
            name (str): Name of the evaluation.

        Returns:
            None
        """
        with open('res.csv', 'a') as file:
            file.write(
                f',,{name}\n,,Name,Resources,Ideal Profit,Real Profit,Sold Resources,Remaining Resources,Percentage '
                f'of sold Resources\n')

            profit = 0
            profit_n = []
            solds = []
            proftis = []
            is_one = True

            for seller in sellers:
                print(f'Seller {seller.name} with {seller.resources} Resources')
                file.write(f',,{seller.name},{seller.resources},')

                ideal_profit_value = self.ideal_profit(seller.resources, buyers)
                file.write(f'{ideal_profit_value},')
                print(f"Ideal Profit: {ideal_profit_value}")

                profit1 = 0
                sold_resources = 0

                for coalition in coalitions:
                    if seller in coalition.sellers:
                        seller_share = coalition.sellers[coalition.sellers.index(seller)]
                        profit1 += seller_share.resources * coalition.buyer.amount_to_pay
                        sold_resources += seller_share.resources

                    if is_one:
                        profit += coalition.buyer.demand * coalition.buyer.amount_to_pay
                        profit_n.extend(ss.name for ss in coalition.sellers if ss.name not in profit_n)

                is_one = False

                print(f"Real Profit: {profit1}")
                file.write(f'{profit1},')
                print(f'Sold Resources: {sold_resources}')
                file.write(f'{sold_resources},')
                print(f'Remaining Resources: {seller.resources - sold_resources}')
                file.write(f'{seller.resources - sold_resources},')
                print(f'Percentage of sold Resources: {sold_resources * 100 / seller.resources}')
                file.write(f"{sold_resources * 100 / seller.resources}\n")
                print('------------------------------')
                solds.append(sold_resources / seller.resources)
                proftis.append(profit1 / ideal_profit_value)

            file.write(f"\n\n,,Ideal Profit,Profit,Gini For Sold Resources,Average For Sold Resources,Gini For Profit,"
                       f"average For Profit,Percentage of Sold Resources,Percentage of Fulfilled Requests,Percentage of "
                       f"Provisioned Resources\n")

            ideal_profit_sum = sum(self.ideal_profit(seller.resources, buyers) for seller in sellers)
            print(f"Ideal Profit: {ideal_profit_sum}")
            file.write(f',,{ideal_profit_sum},')

            print(f"Profit: {profit}")
            file.write(f'{profit},')

            sold_resources_gini = self.gini_coefficient(solds)
            print(f'Gini For Sold Resources: {sold_resources_gini}')
            file.write(f'{sold_resources_gini},')

            average_sold_resources = sum(solds) / len(solds)
            print(f'Average For Sold Resources: {average_sold_resources}')
            file.write(f'{average_sold_resources},')

            profit_gini = self.gini_coefficient(proftis)
            print(f'Gini For Profit: {profit_gini}')
            file.write(f'{profit_gini},')

            average_profit = sum(proftis) / len(proftis)
            print(f'average For Profit: {average_profit}')
            file.write(f'{average_profit},')

            total_sold_resources = sum(
                seller.resources - temp_sellers[temp_sellers.index(seller)].resources for seller in sellers)
            total_resources = sum(seller.resources for seller in sellers)
            print(f"Percentage of Sold Resources: {total_sold_resources * 100 / total_resources}")
            file.write(f'{total_sold_resources * 100 / total_resources},')

            percentage_fulfilled_requests = (len(buyers) - len(temp_buyers)) * 100 / len(buyers)
            print(f"Percentage of Fulfilled Requests: {percentage_fulfilled_requests}")
            file.write(f'{percentage_fulfilled_requests},')

            total_demand = sum(buyer.demand for buyer in buyers)
            demand_provisioned = sum(buyer.demand for buyer in buyers if buyer in temp_buyers)
            percentage_provisioned_resources = (total_demand - demand_provisioned) * 100 / total_demand
            print(f"Percentage of Provisioned Resources: {percentage_provisioned_resources}")
            file.write(f'{percentage_provisioned_resources}\n')


# Example usage
sellers_list = [Seller('S1', 5), Seller('S2', 3), Seller('S3', 6), Seller('S4', 14)]
buyers_list = [Buyer('B1', 7, 100), Buyer('B2', 5, 100), Buyer('B3', 2, 100), Buyer("B4", 10, 100),
               Buyer("B5", 100, 100)]

cgttc = CgTtc()
coalitions, remain_seller, remain_buyers = cgttc.cg_ttc_run(sellers_list, buyers_list)
cgttc.eval_fun(sellers_list, buyers_list, coalitions, remain_seller, remain_buyers, 'CG-TTC')
