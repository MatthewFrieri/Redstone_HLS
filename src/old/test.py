from simplify_expression import SimplifyExpression


minterms = ["0100", "1000", "1010", "1011", "1100", "1111"]
# minterms = ["0000", "0001", "1101", "1111", "1110", "1001", "1011", "1010"]
# minterms = ["000", "100", "001", "011", "111"]
print(SimplifyExpression._get_prime_implicants(minterms))
print()
print(SimplifyExpression.simplify(minterms))
