import sympy
import copy
import numpy as np

s = sympy.symbols('s')

def tolatex(var):
    outstr = sympy.printing.latex(var)
    print(outstr)


def sympy_time_vect(xtsym,t_sym,tvect):
    """Find a vector of floating point numbers for xtsym(t).  
    xtsym is a symbolic expression that needs to be evaluated at each 
    t_i in tvect"""
    N = len(tvect)
    xvect = np.zeros(N)

    for i, t_i in enumerate(tvect):
        xvect[i] = xtsym.subs(t_sym,t_i)

    return xvect


def part_frac_solver(Xs, part_frac, denom, coeff_list):
    """This is my old version from Fall 2016.  The only real issue
    is that if there is a 1/m type term that is intended for the numerator,
    it ends up in Xden and gets lost."""
    part_frac_num = (part_frac*denom).simplify()
    Xnum, Xden = Xs.as_numer_denom()
    num_zero_eqn = part_frac_num-Xnum#assumes denominators are the same on 
        #both sides of the equation
    num_poly = sympy.Poly(num_zero_eqn,s)
    num_coeffs = num_poly.coeffs()
    soln = sympy.solve(num_coeffs,coeff_list)
    return soln


def solve_coeff_lists(rhs_list, lhs_list, coeff_list):
    eqlist = [Ai-Bi for Ai, Bi in zip(rhs_list, lhs_list)]
    sol = sympy.solve(eqlist,coeff_list)
    return sol


def find_den_list(Xpf):
    den_list = []

    for item in Xpf.as_ordered_terms():
        cur_N, cur_D = item.as_numer_denom()
        den_list.append(cur_D)

    return den_list


def find_num_list(Xpf):
    num_list = []

    for item in Xpf.as_ordered_terms():
        cur_N, cur_D = item.as_numer_denom()
        num_list.append(cur_N)

    return num_list


def find_common_denominator(den_list):
    """Check den_list for repeated roots and remove all but the
    highest powers of any repeated real roots.  Return the common
    denominator multiplied out."""
    myden = copy.copy(den_list)

    for item in myden:
        for i in range(1,6):
            j = i+1
            if item**j in myden:
                myden.remove(item**i)

    # myden should now only include the highest powers of
    # repeated terms
    D = myden.pop(0)

    # myden now only includes items 1:end
    for item in myden:
        D *= item

    return D


def explicit_common_denominator(Xpf, comden):
    """Students in 345 in Fall 2017 seemed to find it helpful if I
    explicitly placed all my partial fraction expansion terms over a
    common denominator as part of PFE.  So, I am writing this function
    to do that.  Xpf = N1/D1 + N2/D2 + ..., as_ordered_terms should
    break that into [N1/D1,N2/D2,...].  We are seeking to find
    whatever term we would multiply Ni/Di by to put it over the common
    denominator.  This term is comden/cur_D"""

    big_N = 0

    for item in Xpf.as_ordered_terms():
        cur_N, cur_D = item.as_numer_denom()
        n_i = (comden/cur_D).simplify()
        big_N += cur_N*n_i
    
    Xcd = big_N/comden
    return Xcd
    

def find_num(Xs,comden):
    return (Xs*comden).simplify()


def build_s_poly(expr):
    poly_out = sympy.Poly(expr,s)
    return poly_out


def find_coeffs_of_s(expr):
    mypoly = build_s_poly(expr)
    coeffs = mypoly.coeffs()
    if expr.subs({s:0}) == 0:
        # there is a missing term in coeffs for 0*s**0
        coeffs += [0]
    return coeffs


def verify_coeff_list(expr, coeffs):
    """Verify that each element of coeffs times the appropriate power
    of s gives back expr.  This will help to check for mising coeffs,
    especially if an expression has no s**0 term."""
    N_terms = len(coeffs)
    max_n = N_terms-1

    check = 0
    
    for i, term in enumerate(coeffs):
        cur_term = term*s**(max_n-i)
        check += cur_term

    test = expr - check
    test2 = (test.expand()).simplify()
    return test2


def coeffs_of_s_explicit(expr):
    """Find the coefficients of s in expr explicitly by setting s to 0
    to find the next part and then subtracting that part off and
    dividing by s"""
    expr_rest = copy.copy(expr)
    mydict = {}
    
    for i in range(20):
        next_part = expr_rest.subs({s:0})
        mydict[s**i] = next_part.simplify()
        expr_rest -= next_part
        if expr_rest.simplify() == 0:
            break
        expr_rest = (expr_rest/s).expand()

    return mydict

    
    
class partial_fraction_solver(object):
    """Class to solve parital fraction expansion problems for dynamic
    systems and control"""
    def __init__(self, Xs, Xpf, unknowns):
        """Xs refers to X(s), the thing whose x(t) we are trying to
        find via partial fraction expansion.  Xpf is the partial
        fraction expansion form with unknown coefficients in the
        numerator.  unknowns is the list of unknown coefficients."""
        self.Xs = Xs
        self.Xpf = Xpf
        self.unknowns = unknowns


    def find_common_denominator(self):
        self.den_list = find_den_list(self.Xpf)
        self.comden = find_common_denominator(self.den_list)
        return self.comden

    def find_explicit_common_denom_form(self):
        self.find_common_denominator()
        self.Xcd = explicit_common_denominator(self.Xpf, self.comden)
        return self.Xcd


    def find_numerator_equation(self):
        self.lhs_num = find_num(self.Xs, self.comden)
        self.rhs_num = find_num(self.Xcd, self.comden)
        return sympy.Eq(self.lhs_num, self.rhs_num)


    def expand_numerator_equation(self):
        lhs = self.lhs_num.expand()
        lhs = lhs.simplify()
        rhs = self.rhs_num.expand()
        rhs = rhs.simplify()
        return sympy.Eq(lhs, rhs)


    def find_s_eqns(self):
        # call find_numerator_equation before calling this method
        mydict = {}
        rhs_dict = coeffs_of_s_explicit(self.rhs_num)
        lhs_dict = coeffs_of_s_explicit(self.lhs_num)

        eq_dict = {}

        for key, rval in rhs_dict.items():
            if key in lhs_dict:
                lval = lhs_dict[key]
            else:
                lval = 0

            eq_dict[key] = sympy.Eq(lval,rval)
        
        return eq_dict


    def find_coeffs(self):
        # call find_explicit_common_denom_form before calling this
        # method
        self.find_numerator_equation()
        self.lhs_coeffs = find_coeffs_of_s(self.lhs_num)
        self.rhs_coeffs = find_coeffs_of_s(self.rhs_num)
        

    def pad_lhs_coeffs(self):
        """It seems likely that the numerator of the original form has
        a lower power of s than the common denominator form on the
        right.  Therefore, the coeff list on the left may need to be padded
        with zeros
        """
        n_lhs = len(self.lhs_coeffs)
        n_rhs = len(self.rhs_coeffs)
        n_diff = n_rhs - n_lhs
        if n_diff < 0:
            raise ValueError("lhs coeffs have a higher power of s than the right")
        if n_diff > 0:
            pad = [0] * n_diff
            new_list = pad + self.lhs_coeffs
            self.lhs_coeffs = new_list


    def show_equation(self):
        return sympy.Eq(self.Xs, self.Xpf)
    
        
    def main(self):
        self.find_explicit_common_denom_form()
        self.find_coeffs()
        self.pad_lhs_coeffs()
        test_lhs = verify_coeff_list(self.lhs_num, self.lhs_coeffs)
        assert test_lhs == 0, "Problem with lhs num and coeffs"
        test_rhs = verify_coeff_list(self.rhs_num, self.rhs_coeffs)
        assert test_rhs == 0, "Problem with rhs num and coeffs"
        self.sol = solve_coeff_lists(self.rhs_coeffs, self.lhs_coeffs, \
                                     self.unknowns)
        return self.sol

