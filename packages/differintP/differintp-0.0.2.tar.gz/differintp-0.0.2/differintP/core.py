##############################
#  differintP - v0.0.2


from __future__ import print_function

from typing import Callable, cast

from git import Optional
import numpy as np

from scipy.special import gamma as Gamma


#  CuPy dependency for GPU-accelerated GL_gpu
from .gpu_utils import cupy_manager


def isInteger(n) -> bool:
    if n.imag:
        return False
    if float(n.real).is_integer():
        return True
    else:
        return False


def isPositiveInteger(n) -> bool:
    return isInteger(n) and n > 0


def checkValues(
    alpha: float,
    domain_start: int | float,
    domain_end: int | float,
    num_points: int,
    support_complex_alpha: bool = False
) -> bool | None:
    """Type checking for valid inputs."""

    assert isPositiveInteger(num_points), (
        "num_points is not an integer: %r" % num_points
    )

    assert isinstance(domain_start, (int, np.integer, float, np.floating)), (
        "domain_start must be integer or float: %r" % domain_start
    )

    assert isinstance(domain_end, (int, np.integer, float, np.floating)), (
        "domain_end must be integer or float: %r" % domain_end
    )

    if not support_complex_alpha:
        assert not isinstance(
            alpha, complex
        ), "Complex alpha not supported for this algorithm."

    return


def functionCheck(
    f_name: Callable | list | np.ndarray,
    domain_start: float | int,
    domain_end: float | int,
    num_points: int,
):
    """Check if function is callable and assign function values."""

    # Define the function domain and obtain function values.
    if hasattr(f_name, "__call__"):
        f_name = cast(Callable, f_name)
        # If f_name is callable, call it and save to a list.
        x = np.linspace(domain_start, domain_end, num_points)
        f_values = list(map(lambda t: f_name(t), x))
        step_size = x[1] - x[0]
    else:
        f_name = cast(np.ndarray | list, f_name)
        num_points = np.size(f_name)
        f_values = f_name
        step_size = (domain_end - domain_start) / (num_points - 1)
    return f_values, step_size


def poch(a, n):
    """Returns the Pochhammer symbol (a)_n. a can be any complex or real number
    except the negative integers and 0. n can be any nonnegative real.
    """
    if isPositiveInteger(n):
        # Compute the Pochhammer symbol.
        n = int(n)
        if n == 0:
            return 1.0
        else:
            poch = 1
            for j in range(n):
                poch *= a + j
            return poch

    # if a and a + n are both nonpositive integers, we can use another formula...
    # see here https://www.mathworks.com/help/symbolic/sym.pochhammer.html
    if isPositiveInteger(-1 * a) and isPositiveInteger(-1 * a - n):
        sign = -1 if np.abs(n % 2) == 1 else 1
        return sign * Gamma(1 - a) / Gamma(1 - a - n)
    return Gamma(a + n) / Gamma(a)


def Beta(
    x: int | float | np.ndarray | list | complex,
    y: int | float | np.ndarray | list | complex,
) -> int | float | np.ndarray | list | complex:
    """Beta function using Godfrey's Gamma function."""

    return Gamma(x) * Gamma(y) / Gamma(x + y)  # type: ignore


def MittagLeffler(
    a: float,
    b: float,
    x: np.ndarray,
    num_terms: int = 50,
    ignore_special_cases: bool = False,
) -> np.ndarray:
    """Calculate the Mittag-Leffler function by checking for special cases, and trying to
     reduce the parameters. If neither of those work, it just brute forces it.

     Parameters
    ==========
     a : float
         The first parameter of the Mittag-Leffler function.
     b : float
         The second parameter of the Mittag-Leffler function
     x : 1D-array of floats (can be len = 1)
         The value or values to be evaluated at.
     num_terms : int
         The number of terms to calculate in the sum. Ignored if
         a special case can be used instead. Default value is 100.
     ignore_special_cases : bool
         Don't use the special cases, use the series definition.
         Probably only useful for testing. Default value is False.
    """
    # check for quick special cases
    if not ignore_special_cases:
        if a == 0:
            if (np.abs(x) < 1).all():
                return 1 / Gamma(b) * 1 / (1 - x)
            return x * np.inf
        elif a == 0.5 and b == 1:
            # requires calculation of the complementary error function
            pass
        elif a == 1 and b == 1:
            return np.exp(x)
        elif a == 2 and b == 1:
            return np.cosh(np.sqrt(x))
        elif a == 1 and b == 2:
            return (np.exp(x) - 1) / x
        elif a == 2 and b == 2:
            return np.sinh(np.sqrt(x)) / np.sqrt(x)
    # manually calculate with series definition
    exponents = np.arange(num_terms)
    exp_vals = np.array([x]).T ** exponents
    gamma_vals = np.array([Gamma(exponent * a + b) for exponent in exponents])
    return np.sum(exp_vals / gamma_vals, axis=1)


def GLcoeffs(alpha: float, n: int) -> np.ndarray:
    """Vectorized GL coefficient computation"""
    """ Computes the GL coefficient array of size n.

        These coefficients can be used for both the GL
        and the improved GL algorithm.
    """
    if n == 0:
        return np.array([1.0])

    # Preallocate factors array
    factors = np.ones(n + 1)

    # Compute the multiplicative factors for positions 1 to n
    numerators = -alpha + np.arange(n)
    denominators = np.arange(1, n + 1)
    factors[1:] = numerators / denominators

    # Compute cumulative product
    return np.cumprod(factors)


def GLpoint(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Computes the GL fractional derivative of a function at a point.

    Parameters
    ==========
     alpha : float
         The order of the differintegral to be computed.
     f_name : function handle, lambda function, list, or 1d-array of
              function values
         This is the function that is to be differintegrated.
     domain_start : float
         The left-endpoint of the function domain. Default value is 0.
     domain_end : float
         The right-endpoint of the function domain; the point at which the
         differintegral is being evaluated. Default value is 1.
     num_points : integer
         The number of points in the domain. Default value is 100.

     Examples:
     >>> DF_poly = GLpoint(-0.5, lambda x: 3*x**2 - 9*x + 2)
     >>> DF_sqrt = GLpoint(0.5, lambda x: np.sqrt(x), 0., 1., 100)
    """
    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, _ = functionCheck(f_name, domain_start, domain_end, num_points)

    # Calculate the GL differintegral, avoiding the explicit calculation of
    # the gamma function.
    GL_previous = f_values[1]
    for index in range(2, num_points):
        GL_current = (
            GL_previous * (num_points - alpha - index - 1) / (num_points - index)
            + f_values[index]
        )
        GL_previous = GL_current

    return GL_current * (num_points / (domain_end - domain_start)) ** alpha # type: ignore


def GL(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> np.ndarray:
    """Optimized GL fractional derivative using precomputation"""
    """ Computes the GL fractional derivative of a function for an entire array
        of function values.

        Parameters
       ==========
        alpha : float
            The order of the differintegral to be computed.
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.

        Examples:
        >>> DF_poly = GL(-0.5, lambda x: x**2 - 1)
        >>> DF_sqrt = GL(0.5, lambda x: np.sqrt(x), 0., 1., 100)
    """
    # Domain handling
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Generate points and get function values
    x = np.linspace(domain_start, domain_end, num_points)
    step_size = x[1] - x[0]

    if callable(f_name):
        f_values = f_name(x)
    else:
        f_values = np.asarray(f_name)
        if len(f_values) != num_points:
            raise ValueError("Function array length doesn't match num_points")

    # Precompute coefficients (vectorized)
    b_coeffs = GLcoeffs(alpha, num_points - 1)

    # FFT convolution
    B = np.fft.rfft(b_coeffs, n=num_points)
    F = np.fft.rfft(f_values)
    result = np.fft.irfft(F * B, n=num_points)[:num_points] * step_size**-alpha

    return result


def _gpu_GLcoeffs(
    alpha: float,
    n: int,
) -> np.ndarray:
    """GPU version of GL coefficients"""
    if cupy_manager.HAS_CUPY:
        k = cupy_manager.cp.arange(n + 1)  # type: ignore
        factors = cupy_manager.cp.ones(n + 1)  # type: ignore
        if n > 0:
            numerators = -alpha + cupy_manager.cp.arange(n)  # type: ignore
            denominators = cupy_manager.cp.arange(1, n + 1)  # type: ignore
            factors[1:] = numerators / denominators
        return cupy_manager.cp.cumprod(factors)  # type: ignore
    else:
        raise RuntimeError("CuPy not available")


def GL_gpu(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> np.ndarray:
    """GPU-accelerated GL fractional derivative"""

    """
    GPU-accelerated GL fractional derivative (requires CuPy)

    Note: This function requires CuPy with CUDA support. Install with:
        pip install cupy-cuda11x   or   cupy-cuda12x
        the code is only tested with cupy-cuda12x
    """

    if not cupy_manager.HAS_CUPY:
        raise RuntimeError(
            "CuPy not available. Please install CuPy with CUDA support to use this function.\n"
            "Install via: pip install cupy-cuda11x (replace 11x with your CUDA version)"
        )

    # Convert to GPU arrays
    x = cupy_manager.cp.linspace(domain_start, domain_end, num_points)  # type: ignore
    if callable(f_name):
        f_values = cupy_manager.cp.asarray(f_name(cupy_manager.cp.asnumpy(x)))  # type: ignore
    else:
        f_values = cupy_manager.cp.asarray(f_name)  # type: ignore

    # GPU-accelerated computation
    b_coeffs = _gpu_GLcoeffs(alpha, num_points - 1)
    B = cupy_manager.cp.fft.rfft(b_coeffs)  # type: ignore
    F = cupy_manager.cp.fft.rfft(f_values)  # type: ignore
    result = cupy_manager.cp.fft.irfft(F * B, n=num_points)[:num_points] * (  # type: ignore
        (x[1] - x[0]) ** -alpha
    )

    return cupy_manager.cp.asnumpy(result)  # Convert back to CPU # type: ignore


def GLI(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> np.ndarray:
    """Computes the 'improved' GL fractional derivative of a function for an
     entire array of function values. The 'improved' definition uses the
     3-point Lagrange interpolation found in:

         Oldham, K. & Spanier, J. (1974). The Fractional Calculus: Theory
             and Applications of Differentiation and Integration to Arbitrary
             Order. Academic Press, Inc.

     Parameters
    ==========
     alpha : float
         The order of the differintegral to be computed.
     f_name : function handle, lambda function, list, or 1d-array of
              function values
         This is the function that is to be differintegrated.
     domain_start : float
         The left-endpoint of the function domain. Default value is 0.
     domain_end : float
         The right-endpoint of the function domain; the point at which the
         differintegral is being evaluated. Default value is 1.
     num_points : integer
         The number of points in the domain. Default value is 100.

     Examples:
     >>> GLI_poly = GLI(-0.5, lambda x: x**2 - 1)
     >>> GLI_sqrt = GLI(0.5, lambda x: np.sqrt(x), 0., 1., 100)
    """

    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, step_size = functionCheck(f_name, domain_start, domain_end, num_points)

    # Get interpolating values.
    IN = GLIinterpolat(0.5)
    I = [IN.prv, IN.crr, IN.nxt]

    # Get array of generalized binomial coefficients.
    b_coeffs = GLcoeffs(0.5, num_points)

    # Calculate the improved GL differintegral using convolution.
    GLI = np.zeros(num_points)
    for i in range(3, num_points):
        F = f_values[:i]
        L = len(F)
        B = b_coeffs[: (L - 2)]
        G = np.convolve(F, B, "valid")
        GLI[i] = sum(G * I)

    return GLI * step_size**-alpha


def CRONE(alpha, f_name):
    """Calculates the GL derivative approximation using the CRONE operator.



    see Mathieu, B., Melchior, P., Oustaloup, A., and Ceyral, Ch. (2003). Fractional
        differentiation for edge detection. Signal Processing, 83, pp. 2421 -- 2432.

    """

    class Error(Exception):
        pass

    class InputError(Error):
        def __init__(self, expr, msg):
            self.expr = expr
            self.msg = msg

    def CRONEfilter(siz, alpha):
        """Creates CRONE convolution filter."""

        if (siz % 2) != 0:
            w = siz
            stop = int((siz - 1) / 2)
            print(stop)
        else:
            w = siz + 1
            stop = int(siz / 2)

        D = GLcoeffs(alpha, stop)
        D1 = D
        D = np.flip(D, axis=0)

        np.append(D, 0)
        np.append(D, -D1)

        return D

    if len(np.shape(f_name)) > 1:
        [rows, cols] = np.shape(f_name)
        imgx = np.zeros((rows, cols))
        imgy = np.zeros((rows, cols))

        # Define the CRONE operators with the correct sizes.
        CRONEx = CRONEfilter(cols, alpha)  # cols is the width of the matrix
        CRONEy = CRONEfilter(rows, alpha)  # rows is the height of the matrix

        for i in range(rows):
            imgx[i, :] = np.convolve(f_name[i, :], CRONEx, mode="same")

        for j in range(cols):
            imgy[:, j] = np.convolve(f_name[:, j], CRONEy, mode="same")

        return imgx, imgy

    elif len(np.shape(f_name)) == 1:
        w = len(f_name)
        CRONEx = CRONEfilter(w, alpha)  # w is the length of the array

        imgx = np.convolve(f_name, CRONEx, mode="same")

        return imgx

    else:
        raise InputError(f_name, "f_name must have dimension <= 2")


def RLmatrix(alpha, N):
    """Vectorized RL coefficient matrix generation"""
    # Precompute all required powers
    k = np.arange(N)
    v = np.zeros(N + 2)  # +2 to avoid index issues
    v[1:] = np.power(np.arange(1, N + 2), 1 - alpha)

    # Initialize coefficient matrix
    coeffMatrix = np.zeros((N, N))

    # Set diagonal to 1
    np.fill_diagonal(coeffMatrix, 1)

    # First column (j=0)
    i_vals = np.arange(1, N)
    coeffMatrix[i_vals, 0] = v[i_vals - 1] - (i_vals + alpha - 1) * np.power(
        i_vals, -alpha
    )

    # Main coefficients using vectorization
    for k_val in range(1, N - 1):
        rows = np.arange(k_val + 1, N)
        cols = rows - k_val
        coeffMatrix[rows, cols] = v[k_val + 1] + v[k_val - 1] - 2 * v[k_val]

    # Normalize with Gamma function
    return coeffMatrix / Gamma(2 - alpha)


def RLcoeffs(index_k, index_j, alpha):
    """Calculates coefficients for the RL differintegral operator.

    see Baleanu, D., Diethelm, K., Scalas, E., and Trujillo, J.J. (2012). Fractional
        Calculus: Models and Numerical Methods. World Scientific.
    """
    """Calculate the RL differintegral at a point with the trapezoid rule.

    Parameters
       ==========
        alpha : float
            The order of the differintegral to be computed.
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.

        Examples:
        >>> RL_sqrt = RLpoint(0.5, lambda x: np.sqrt(x))
        >>> RL_poly = RLpoint(0.5, lambda x: x**2 - 4*x - 1, 0., 1., 100)
    """
    if index_j == 0:
        return (index_k - 1) ** (1 - alpha) - (index_k + alpha - 1) * index_k**-alpha
    elif index_j == index_k:
        return 1
    else:
        return (
            (index_k - index_j + 1) ** (1 - alpha)
            + (index_k - index_j - 1) ** (1 - alpha)
            - 2 * (index_k - index_j) ** (1 - alpha)
        )


def RLpoint(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Optimized RL fractional derivative calculation 8x - 60x speed"""
    """Calculate the RL differintegral at a point with the trapezoid rule.

    Parameters
       ==========
        alpha : float
            The order of the differintegral to be computed.
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.

        Examples:
        >>> RL_sqrt = RLpoint(0.5, lambda x: np.sqrt(x))
        >>> RL_poly = RLpoint(0.5, lambda x: x**2 - 4*x - 1, 0., 1., 100)
    """

    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Generate evaluation points
    x = np.linspace(domain_start, domain_end, num_points)
    step_size = x[1] - x[0]

    # Get function values (optimized)
    if callable(f_name):
        f_values = f_name(x)
    else:
        f_values = np.asarray(f_name)
        if len(f_values) != num_points:
            raise ValueError("Function array length doesn't match num_points")

    # Precompute all coefficients in vectorized form
    k = num_points - 1  # Fixed evaluation index (endpoint)
    j = np.arange(num_points)

    # Initialize coefficient array
    coeffs = np.zeros(num_points)

    # Case 1: j == 0
    mask_j0 = j == 0
    if k > 0:  # Only compute if k > 0
        coeffs[mask_j0] = (k - 1) ** (1 - alpha) - (k + alpha - 1) * k**-alpha

    # Case 2: j == k
    mask_jk = j == k
    coeffs[mask_jk] = 1

    # Case 3: All other indices
    mask_other = ~mask_j0 & ~mask_jk
    d = k - j[mask_other]
    coeffs[mask_other] = (
        (d + 1) ** (1 - alpha) + (d - 1) ** (1 - alpha) - 2 * d ** (1 - alpha)
    )

    # Final calculation
    C = 1 / Gamma(2 - alpha)
    return C * step_size**-alpha * np.dot(coeffs, f_values)


def RL(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> np.ndarray:
    """Optimized RL fractional derivative calculation 14x speed"""
    """ Calculate the RL algorithm using a trapezoid rule over
        an array of function values.

    Parameters
    ==========
        alpha : float
            The order of the differintegral to be computed.
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.

    Output
    ======
        RL : float 1d-array
            Each element of the array is the RL differintegral evaluated at the
            corresponding function array index.

    Examples:
        >>> RL_sqrt = RL(0.5, lambda x: np.sqrt(x))
        >>> RL_poly = RL(0.5, lambda x: x**2 - 1, 0., 1., 100)
    """
    # Domain validation and flipping
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Generate evaluation points
    x = np.linspace(domain_start, domain_end, num_points)
    step_size = x[1] - x[0]

    # Get function values (optimized)
    if callable(f_name):
        f_values = f_name(x)
    else:
        f_values = np.asarray(f_name)
        if len(f_values) != num_points:
            raise ValueError("Function array length doesn't match num_points")

    # Compute RL differintegral
    D = RLmatrix(alpha, num_points)
    result = step_size**-alpha * (D @ f_values)
    return result


class GLIinterpolat:
    """Class for computing interpolation of function values for the
    improved GL algorithm.

    Using a class here helps avoid type flexibility for these constants.
    """

    def __init__(self, alpha):
        # Determine coefficients for quadratic interpolation.
        self.nxt = alpha * (2 + alpha) / 8
        self.crr = (4 - alpha * alpha) / 4
        self.prv = alpha * (alpha - 2) / 8


def CaputoL1point(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Calculate the Caputo derivative of a function at a point using the L1 method.

    see Karniadakis, G.E.. (2019). Handbook of Fractional Calculus with Applications
    Volume 3: Numerical Methods. De Gruyter.

    Parameters
    ==========
        alpha : float
            The order of the differintegral to be computed. Must be in (0, 1)
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.
    Output
    ======
        L1 : float
            The Caputo L1 integral evaluated at the corresponding point.
    """

    if alpha <= 0 or alpha >= 1:
        raise ValueError("Alpha must be in (0, 1) for this method.")

    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, step_size = functionCheck(f_name, domain_start, domain_end, num_points)

    f_values = np.array(f_values)
    j_values = np.arange(0, num_points - 1)
    coefficients = (j_values + 1) ** (1 - alpha) - (j_values) ** (1 - alpha)
    f_differences = f_values[1:] - f_values[:-1]
    f_differences = f_differences[::-1]
    L1 = (
        1
        / Gamma(2 - alpha)
        * np.sum(np.multiply(coefficients * step_size ** (-alpha), f_differences))
    )

    return L1


def CaputoL2point(
    alpha: float,
    f_name: Callable,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Calculate the Caputo derivative of a function at a point using the L2 method.
        A note: this method requires evaluation of the point f(domain_end + step size),
        and currently will only work if `f_name` is a callable function.

    see Karniadakis, G.E.. (2019). Handbook of Fractional Calculus with Applications
    Volume 3: Numerical Methods. De Gruyter.

    Parameters
    ==========
        alpha : float
            The order of the differintegral to be computed. Must be in (1, 2).
        f_name : function handle or lambda function
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.
    Output
    ======
        L2 : float
            The Caputo L2 integral evaluated at the corresponding point.
    """
    if alpha <= 1 or alpha >= 2:
        raise ValueError("Alpha must be in (1, 2) for this method.")
    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, step_size = functionCheck(f_name, domain_start, domain_end, num_points)

    def b_coes(alpha, j):
        return (j + 1) ** (2 - alpha) - j ** (2 - alpha)

    # start with the point outside of the domain
    L2 = b_coes(alpha, 0) * (
        f_values[num_points - 2]
        + f_name(num_points * step_size)
        - 2 * f_values[num_points - 1]
    )  # f_name(num_points * step_size)
    for k in range(1, num_points - 1):
        L2 += b_coes(alpha, k) * (
            f_values[num_points - 2 - k]
            + f_values[num_points - k]
            - 2 * f_values[num_points - k - 1]
        )
    return L2 * step_size ** (-1 * alpha) / Gamma(3 - alpha)


def CaputoL2Cpoint(
    alpha: float,
    f_name: Callable,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Calculate the Caputo derivative of a function at a point using the L2C method.
        A note: this method requires evaluation of the points f(domain_end + step size)
        and f(-step_size), and currently will only work if `f_name` is a callable
        function.

    see Karniadakis, G.E.. (2019). Handbook of Fractional Calculus with Applications
    Volume 3: Numerical Methods. De Gruyter.

    Parameters
    ==========
        alpha : float
            The order of the differintegral to be computed. Must be in (0, 2).
        f_name : function handle or lambda function
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.
    Output
    ======
        L2C : float
            The Caputo L2C integral evaluated at the corresponding point.
    """
    if alpha <= 0 or alpha >= 2:
        raise ValueError("Alpha must be in (0, 1) or (1, 2) for this method.")

    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, step_size = functionCheck(f_name, domain_start, domain_end, num_points)

    def b_coes(alpha, j):
        return (j + 1) ** (2 - alpha) - j ** (2 - alpha)

    # start with the points outside of the domain
    L2C = b_coes(alpha, 0) * (
        f_values[num_points - 3]
        - f_values[num_points - 2]
        - f_values[num_points - 1]
        + f_name(num_points * step_size)
    )  # f_name(num_points * step_size)
    L2C += b_coes(alpha, num_points - 2) * (
        f_name(-1 * step_size) + f_values[2] - f_values[1] - f_values[0]
    )
    for k in range(1, num_points - 2):
        L2C += b_coes(alpha, k) * (
            f_values[num_points - 3 - k]
            - f_values[num_points - k - 2]
            - f_values[num_points - k - 1]
            + f_values[num_points - k]
        )
    L2C *= step_size ** (-1 * alpha) / Gamma(3 - alpha) * 0.5

    return L2C


def CaputoFromRLpoint(
    alpha: float,
    f_name: Callable | np.ndarray | list,
    domain_start: float = 0.0,
    domain_end: float = 1.0,
    num_points: int = 100,
) -> float:
    """Calculate the Caputo derivative of a function at a point using the conversion
        formula from the RL differintegrals. DOESN'T CURRENTLY WORK.

    see Du, R., Yan, Y. and Liang, Z., (2019). A high-order scheme to
        approximate the caputo fractional derivative and its application
        to solve the fractional diffusion wave equation, Journal of
        Computational Physics, 376, pp. 1312-1330

    Parameters
    ==========
        alpha : float
            The order of the differintegral to be computed. Must be in (1, 2).
        f_name : function handle, lambda function, list, or 1d-array of
                 function values
            This is the function that is to be differintegrated.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.
    Output
    ======
        C : float
            The Caputo integral evaluated at the corresponding point.
    """
    if alpha <= 1 or alpha >= 2:
        raise ValueError("Alpha must be in (1, 2) for this method.")

    # Flip the domain limits if they are in the wrong order.
    if domain_start > domain_end:
        domain_start, domain_end = domain_end, domain_start

    # Check inputs.
    checkValues(alpha, domain_start, domain_end, num_points)
    f_values, step_size = functionCheck(f_name, domain_start, domain_end, num_points)

    C = 0
    C -= f_values[0] * domain_end ** (-1 * alpha) / Gamma(1 - alpha)
    C -= (
        (f_values[1] - f_values[0])
        / step_size
        * domain_end ** (1 - alpha)
        / Gamma(2 - alpha)
    )
    C += (
        RLpoint(
            alpha - 2, f_name, domain_start, float(domain_end + step_size), num_points
        )
        / step_size**2
    )
    C -= (
        2
        * RLpoint(alpha - 2, f_name, domain_start, float(domain_end), num_points)
        / step_size**2
    )
    C -= (
        RLpoint(
            alpha - 2, f_name, domain_start, float(domain_end - step_size), num_points
        )
        / step_size**2
    )
    return C


def PCcoeffs(alpha, j, n):
    if 1 < alpha:
        if j == 0:
            return (
                (n + 1) ** alpha * (alpha - n)
                + n**alpha * (2 * n - alpha - 1)
                - (n - 1) ** (alpha + 1)
            )
        elif j == n:
            return 2 ** (alpha + 1) - alpha - 3
        return (
            (n - j + 2) ** (alpha + 1)
            + 3 * (n - j) ** (alpha + 1)
            - 3 * (n - j + 1) ** (alpha + 1)
            - (n - j - 1) ** (alpha + 1)
        )


def PCsolver(
    initial_values, alpha, f_name, domain_start=0, domain_end=1, num_points=100
):
    """Solve an equation of the form D[y(x)]=f(x, y(x)) using the predictor-corrector
        method, modified to be compatible with fractional derivatives.

    see Deng, W. (2007) Short memory principle and a predictor-corrector approach for
        fractional differential equations. Journal of Computational and Applied
        Mathematics.

    test examples from
        Baskonus, H.M., Bulut, H. (2015) On the numerical solutions of some fractional
        ordinary differential equations by fractional Adams-Bashforth-Moulton method.
        De Gruyter.
        Weilbeer, M. (2005) Efficient Numerical Methods for Fractional Differential
        Equations and their Analytical Background.

    Parameters
    ==========
        initial_values : float 1d-array
            A list of initial values for the IVP. There should be as many IVs
            as ceil(alpha).
        alpha : float
            The order of the differintegral in the equation to be computed.
        f_name : function handle or lambda function
            This is the function on the right side of the equation, and should
            accept two variables; first the independant variable, and second
            the equation to be solved.
        domain_start : float
            The left-endpoint of the function domain. Default value is 0.
        domain_end : float
            The right-endpoint of the function domain; the point at which the
            differintegral is being evaluated. Default value is 1.
        num_points : integer
            The number of points in the domain. Default value is 100.

    Output
    ======
        y_correction : float 1d-array
            The calculated solution to the IVP at each of the points
            between the left and right endpoint.

    Examples:
        >>> f_name = lambda x, y : y - x - 1
        >>> initial_values = [1, 1]
        >>> y_solved = PCsolver(initial_values, 1.5, f_name)
        >>> theoretical = np.linspace(0, 1, 100) + 1
        >>> np.allclose(y_solved, theoretical)
        True
    """
    from scipy.special import factorial

    x_points = np.linspace(domain_start, domain_end, num_points)
    step_size = x_points[1] - x_points[0]
    y_correction = np.zeros(num_points, dtype="complex")
    y_prediction = np.zeros(num_points, dtype="complex")

    y_prediction[0] = initial_values[0]
    y_correction[0] = initial_values[0]
    for x_index in range(num_points - 1):
        initial_value_contribution = 0
        if 1 < alpha and alpha < 2:
            initial_value_contribution = initial_values[1] * step_size
        elif 2 < alpha:
            for k in range(1, int(np.ceil(alpha))):
                initial_value_contribution += (
                    initial_values[k]
                    / factorial(k)
                    * (x_points[x_index + 1] ** k - x_points[x_index] ** k)
                )
        elif alpha < 1:
            raise ValueError("Not yet supported!")
        y_prediction[x_index + 1] += initial_value_contribution
        y_prediction[x_index + 1] += y_correction[x_index]
        y_prediction[x_index + 1] += (
            step_size**alpha
            / Gamma(alpha + 1)
            * f_name(x_points[x_index], y_correction[x_index])
        )
        subsum = 0
        for j in range(x_index + 1):
            subsum += PCcoeffs(alpha, j, x_index) * f_name(x_points[j], y_correction[j])
        y_prediction[x_index + 1] += step_size**alpha / Gamma(alpha + 2) * subsum

        y_correction[x_index + 1] += initial_value_contribution
        y_correction[x_index + 1] += y_correction[x_index]
        y_correction[x_index + 1] += (
            step_size**alpha
            / Gamma(alpha + 2)
            * alpha
            * f_name(x_points[x_index], y_correction[x_index])
        )
        y_correction[x_index + 1] += (
            step_size**alpha
            / Gamma(alpha + 2)
            * f_name(x_points[x_index + 1], y_prediction[x_index + 1])
        )
        y_correction[x_index + 1] += step_size**alpha / Gamma(alpha + 2) * subsum

    return y_correction
