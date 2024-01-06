# CG-TTC Resource Allocation System

The Cooperative Game - Top Trading Cycle (CG-TTC) is a Python-based resource allocation system designed to facilitate trade between multiple sellers and buyers, forming coalitions to maximize utility and revenue. This implementation is built upon cooperative game theory concepts and focuses on fair and efficient resource distribution.

## Description

The CG-TTC system is a set of Python classes that represent entities in a marketplace, including sellers, buyers, and coalitions. It uses the concept of the Shapley value for fair distribution of coalition revenues and implements the CG-TTC algorithm for resource allocation. This system is suitable for scenarios where multiple parties are involved in the trade of resources and are looking for an optimal coalition to maximize their outcomes.

## Features

- **Seller and Buyer Classes**: Represent the participants in the marketplace with resources and demands.
- **Coalition Class**: Represents the group of sellers fulfilling a buyer's demand.
- **CG-TTC Algorithm Implementation**: Encapsulates the logic for the coalition formation and resource allocation.
- **Shapley Value Calculation**: Ensures fair distribution of revenue among coalition members.
- **Gini Coefficient Calculation**: Measures the inequality in distribution among participants.
- **Performance Evaluation**: Includes functionality to evaluate and log the performance of the algorithm.

## Installation

Ensure you have Python installed on your system. Clone this repository or download the files directly to get started.

```bash
git clone https://github.com/mobin79-stack/CG-TTC
```

## Usage

To run the CG-TTC system, define a list of sellers and buyers with their respective resources and demands. Then, initialize and run the CG-TTC algorithm to see the results.

Example usage:

```python
# Define sellers with their resources
sellers_list = [Seller('S1', 5), Seller('S2', 3), Seller('S3', 6), Seller('S4', 14)]

# Define buyers with their demand and the amount they are willing to pay
buyers_list = [Buyer('B1', 7, 100), Buyer('B2', 5, 100), Buyer('B3', 2, 100), Buyer("B4", 10, 100), Buyer("B5", 100, 100)]

# Initialize the CG-TTC system and run the auction
cgttc = CgTtc()
coalitions, remain_seller, remain_buyers = cgttc.cg_ttc_run(sellers_list, buyers_list)

# Evaluate the performance of the auction
cgttc.eval_fun(sellers_list, buyers_list, coalitions, remain_seller, remain_buyers, 'CG-TTC')
```
