from typing import Tuple, Union, Optional, Dict, Any, List
import math
import numpy as np
from scipy.integrate import odeint, trapezoid
from scipy.optimize import minimize
import time

from .. import error, warning, info, debug, trace

Fitparams = List[float]
def roundifnotnone(val:Optional[float], digits=2, unit=None):
    return None if val is None else f"{round(val, digits)}{'' if unit is None else ' '+unit}"
class Parameters():
    """The parameters describing a drop.

    This class stores the parameters describing the drop in the image
    (gravity angle, tip position in px, radius of curvation in px, capillary length in px).
    It also stores physically relevant informations, such as the pixel-to-mm conversion constant, the acceleration of gravity, the density ratio between the two fluids.

    It can return all these parameters and equivalent ondes (bond number, surface tension) in different units.

    Use :meth:`describe <pypendentdrop.Parameters.describe>` to print the values of the parameters.

    *This class has no public attributes, you should use the (numerous) getter and setter methods to manipulate the variables.*

    This class has str and repr methods #todo add exemples of what this means here.
    """
    RAD_PER_DEG = np.pi/180
    DEG_PER_RAD = 180/np.pi

    def __init__(self):
        self._a_rad: Optional[float] = None
        self._x_px: Optional[float] = None
        self._y_px: Optional[float] = None
        self._r_px: Optional[float] = None
        self._l_px: Optional[float] = None

        self._px_per_mm: Optional[float] = None
        self._d: Optional[float] = 1.00 # delta rho in kg/l
        self._g: Optional[float] = 9.81 # g in m/s2

    def __repr__(self) -> str:
        return f""" 
        pixel density: {roundifnotnone(self.get_px_density(), digits=2, unit='px/mm')}
        gravity: {roundifnotnone(self.get_gravityacc(), digits=3)}
        Delta rho: {roundifnotnone(self.get_densitycontrast(), digits=3)}
        -----
        gravity_angle: {roundifnotnone(self.get_a_deg(), digits=2, unit='deg')} ({roundifnotnone(self.get_a_rad(), digits=4, unit='rad')})
        x_tip_position: {roundifnotnone(self.get_x_px(), digits=2, unit='px')}
        y_tip_position: {roundifnotnone(self.get_y_px(), digits=2, unit='px')}
        r0: {roundifnotnone(self.get_r_mm(), digits=4, unit='mm')} ({roundifnotnone(self.get_r_px(), digits=2, unit='px')})
        capillary_length: {roundifnotnone(self.get_l_mm(), digits=4, unit='mm')} ({roundifnotnone(self.get_l_px(), digits=2, unit='px')})
        """
    def __str__(self) -> str:
        return f"(px_per_mm={self.get_px_density()} ; g={self.get_g()} ; Deltarho={self.get_d()} | a={self.get_a_deg()} deg; x={self.get_x_px()} px; y={self.get_y_px()} px; r={self.get_r_mm()} mm; l={self.get_l_mm()} mm)"

    def describe(self, printfn=print, descriptor = None) -> None:
        """Prints the parameters in the console in a human-friendly fashion.

        Parameters
        ----------
        printfn : function
            The function that will be used to print. By default, print, but you can feed it a logging or debug function.
        descriptor : str
            A short description of this parameter object ('estimated', 'guessed', 'optimized' ...)

        """
        """"""
        printfn(f"Parameters {'' if descriptor is None else ('(' + descriptor + ')')}" + repr(self))

    ###### PIXEL SPACING / SIZE / DENSITY
    def get_px_density(self) -> float:
        """Get the density of pixels, in px/mm. Use ``set_px_density`` to set it.
        
        The pixel density corresponds to the quantity of pixels per unit length in your image.
        For example, if in your image 5 pixels span a length corresponding to 2 mm, the pixel density is 5/2=2.5 pixel per millimeter.
        
        The higher the pixel density, the more zoomed the image is, and in general the better the measurement. 
        A typical pixel density of 100 or higher is recommended for an optimal measurement.
        """
        return self._px_per_mm
    def set_px_density(self, pixel_density:float) -> None:
        self._px_per_mm = pixel_density
    def get_px_spacing(self) -> float:
        """Get the spacing between pixels, in mm. Use ``set_px_spacing`` to set it.
        
        The pixel spacing is to the physical distance corresponding to the space between two adjacent pixels in your image.
        For example, if in your image 5 pixels span a length corresponding to 2 mm, the pixel spacing is 2/5=0.4 millimeter per pixel.
        """
        return None if ((self._px_per_mm or 0) == 0) else 1/self._px_per_mm
    def set_px_spacing(self, pixel_spacing:float) -> None:
        self._px_per_mm = None if ((pixel_spacing or 0) == 0) else 1/pixel_spacing

    ### ANGLE OF GRAVITY SHORT VERSION
    def get_a_rad(self) -> float:
        return self._a_rad
    def set_a_rad(self, gravity_angle_rad:float) -> None:
        self._a_rad = gravity_angle_rad
    def get_a_deg(self) -> float:
        return None if self._a_rad is None else self._a_rad * self.DEG_PER_RAD
    def set_a_deg(self, gravity_angle_deg:float) -> None:
        self._a_rad = None if gravity_angle_deg is None else gravity_angle_deg * self.RAD_PER_DEG

    ### ANGLE OF GRAVITY LONG VERSION
    def get_angleofgravity_rad(self) -> float:
        """Returns the current angle of gravity, in radians. Use ``set_angleofgravity_rad`` to set it manually."""
        return self._a_rad
    def set_angleofgravity_rad(self, gravity_angle_rad:float) -> None:
        """Manually sets the angle of gravity, in radians, to the given value."""
        self._a_rad = gravity_angle_rad
    def get_angleofgravity_deg(self) -> float:
        """Returns the current angle of gravity, in degrees. Use ``set_angleofgravity_deg`` to set it manually."""
        return None if self._a_rad is None else self._a_rad * self.DEG_PER_RAD
    def set_angleofgravity_deg(self, gravity_angle_deg:float) -> None:
        """Manually sets the angle of gravity, in degrees, to the given value."""
        self._a_rad = None if gravity_angle_deg is None else gravity_angle_deg * self.RAD_PER_DEG

    ###### TIP POSITION SHORT VERSION
    def set_x_px(self, x_tip_position_px:float) -> None:
        self._x_px = x_tip_position_px
    def get_x_px(self) -> float:
        return self._x_px
    def set_y_px(self, y_tip_position_px:float) -> None:
        self._y_px = y_tip_position_px
    def get_y_px(self) -> float:
        return self._y_px
    def set_xy_px(self, xy_tip_position_px:float) -> None:
        self._x_px, self._y_px = xy_tip_position_px
    def get_xy_px(self) -> Tuple[float, float]:
        return (self._x_px, self._y_px)

    ### TIP POSITION LONG VERSION
    def set_xtippos_px(self, x_tip_position_px:float) -> None:
        self._x_px = x_tip_position_px
    def get_xtippos_px(self) -> float:
        return self._x_px
    def set_ytippos_px(self, y_tip_position_px:float) -> None:
        self._y_px = y_tip_position_px
    def get_ytippos_px(self) -> float:
        """Get the y position of the tip, in pixels. Use ``set_xytippos_px`` to set it."""
        return self._y_px
    def set_xytippos_px(self, xy_tip_position_px:float) -> None:
        self._x_px, self._y_px = xy_tip_position_px
    def get_xytippos_px(self) -> Tuple[float, float]:
        """Get the (x, y) position of the tip, in pixels. Use ``set_xytippos_px`` to set it."""
        return (self._x_px, self._y_px)

    ### TIP RADIUS OF CURVATURE SHORT VERSION
    def get_r_px(self) -> float:
        return self._r_px
    def set_r_px(self, r0_px:float) -> None:
        self._r_px = r0_px
    def get_r_mm(self) -> float:
        return None if (self._px_per_mm is None or self._r_px is None) else self._r_px / self._px_per_mm
    def set_r_mm(self, r0_mm:float) -> None:
        self._r_px = None if (r0_mm is None or self._px_per_mm is None) else r0_mm * self._px_per_mm

    ### TIP RADIUS OF CURVATURE LONG VERSION
    def get_tipradius_px(self) -> float:
        """
        Returns the radius of curvature at the tip of the drop, in pixels.

        Use :meth:`describe <pypendentdrop.Parameters.set_tipradius_px>` to set this value manually.

        Returns
        -------
        r0_px : float
            The tip radius, in pixels.
        """
        return self._r_px
    def set_tipradius_px(self, r0_px:float) -> None:
        """
        Manually sets the radius of curvature at the tip of the drop, in pixels.

        Parameters
        ----------
        r0_px : float
            The tip radius, in pixels.
        """
        self._r_px = r0_px
    def get_tipradius_mm(self) -> float:
        """Get the radius of curvature at the tip, in millimeters. Use ``set_tipradius_mm`` to set it."""
        return None if (self._px_per_mm is None or self._r_px is None) else self._r_px / self._px_per_mm
    def set_tipradius_mm(self, r0_mm:float) -> None:
        self._r_px = None if (r0_mm is None or self._px_per_mm is None) else r0_mm * self._px_per_mm

    ### CAPILLARY LENGTH SHORT VERSION
    def get_l_px(self) -> float:
        return self._l_px
    def set_l_px(self, lcap_px:float) -> None:
        self._l_px = lcap_px
    def get_l_mm(self) -> float:
        return None if (self._px_per_mm is None or self._l_px is None) else self._l_px / self._px_per_mm
    def set_l_mm(self, lcap_mm:float) -> None:
        self._l_px = None if (lcap_mm is None or self._px_per_mm is None) else lcap_mm * self._px_per_mm

    ### CAPILLARY LENGTH LONG VERSION
    def get_caplength_mm(self) -> float:
        """
        Returns the capillary length, in millimeters.

        Use :meth:`describe <pypendentdrop.Parameters.set_caplength_mm>` to set this value manually.

        Returns
        -------
        lcap_mm : float
            The capillary length, in millimeters.
        """
        return self.get_l_mm()
    def set_caplength_mm(self, lcap_mm:float):
        """
        Manually sets the capillary length, in millimeters.

        Parameters
        ----------
        lcap_mm : float
            The capillary length, in millimeters.
        """
        self.set_l_mm(lcap_mm=lcap_mm)
    def get_caplength_px(self) -> float:
        """
        Returns the capillary length, in pixels.

        Use :meth:`describe <pypendentdrop.Parameters.set_caplength_px>` to set this value manually.

        Returns
        -------
        lcap_px : float
            The capillary length, in pixels.
        """
        return self.get_l_px()
    def set_caplength_px(self, lcap_px:float) -> None:
        """
        Manually sets the capillary length, in pixels.

        Parameters
        ----------
        lcap_px : float
            The capillary length, in pixels.
        """
        self.set_l_px(lcap_px=lcap_px)

    ### GRAVITY ACCELERATION SHORT VERSION
    def set_g(self, g:Optional[float]) -> None:
        self._g = g
    def get_g(self):
        return self._g

    ### GRAVITY ACCELERATION LONG VERSION
    def set_gravityacc(self, g:Optional[float]) -> None:
        """Sets the value for the acceleration of gravity for this experiment.

        Parameters
        ----------
        g : float
            The acceleration of gravity, in m/s^2
        """
        self._g = g
    def get_gravityacc(self):
        """Returns the acceleration of gravity for this experiment.

        Use :meth:`describe <pypendentdrop.Parameters.set_gravityacc>` to modify this value.

        Returns
        -------
        g : float
            The acceleration of gravity, in m/s^2.
            The default value is 9.81.
        """
        return self._g

    ### DENSITY CONTRAST SHORT VERSION
    def set_d(self, densitycontrast_kgL:Optional[float]) -> None:
        self._d = densitycontrast_kgL
    def get_d(self):
        return self._d

    ### DENSITY CONTRAST LONG VERSION
    def set_densitycontrast(self, densitycontrast_kgL:Optional[float]) -> None:
        self._d = densitycontrast_kgL
    def get_densitycontrast(self):
        """Get the density contrast between the fluids, in kg/L (typically 1 for water/air). Use ``set_densitycontrast`` to set it."""
        return self._d
    def get_dimensionlessTipRadius(self):
        return None if (self._r_px is None or self._l_px is None) else self._r_px / self._l_px

    def get_fitparams(self) -> Fitparams:
        """Returns the parameters in a ``scipy.minimize``-friendly way."""
        return [self.get_a_rad(), self.get_x_px(), self.get_y_px(), self.get_r_px(), self.get_l_px()]

    def can_show_tip_position(self) -> bool:
        x_is_ok = not( (self.get_x_px() or 0) == 0 )
        y_is_ok = not( (self.get_y_px() or 0) == 0 )
        return x_is_ok * y_is_ok
    def can_estimate(self) -> bool:
        """Decides if an auto-estimation of the parameters is possible."""
        return not( (self.get_px_density() or 0) == 0 )
    def can_optimize(self) -> bool:
        """Decides if an optimization of the parameters is possible."""
        r0_is_ok = not( (self.get_r_px() or 0) == 0 )
        lcap_is_ok = not( (self.get_l_px() or 0) == 0 )
        px_density_is_ok = not( (self.get_px_density() or 0) == 0 )
        return r0_is_ok * lcap_is_ok * px_density_is_ok

    def get_bond(self):
        """Returns the Bond number (square of the (tip radius)/(capillary length) ratio)"""
        return None if (self._r_px is None or self._l_px is None) else (self._r_px / self._l_px)**2

    def get_surface_tension_mN(self):
        """Returns the surface tension in mN (or None if it cannot be computed)."""
        return None if ((self.get_g() is None) or (self.get_d() is None) or (self.get_l_mm() is None)) else (self.get_d() * self.get_g() * self.get_l_mm()**2)


# paremeters
def image_centre(image:np.ndarray) -> np.ndarray:
    """
    Returns the (x, y) coordinates of the center of an image (around which it is pertinent to rotate the contour).

    :param image:
    :return:
    """
    return np.array(image.shape[1::-1]) / 2

def getrotationandscalematrix(centre, angle:float=0., scalefactor:float=1.):
    """
    Gets the matrix allowing the rotation and scaling of a contour (or an image) around a point.
    Shamelessly inspired from OpenCV's cv2.getRotationMatrix2D.

    :param centre:
    :param angle:
    :param scalefactor:
    :return:
    """
    c = math.cos(angle) * scalefactor
    s = math.sin(angle) * scalefactor
    return np.array([[c, s, (1-c)*centre[0] - s*centre[1]],
                     [-s, c, s*centre[0] + (1-c)*centre[1]]])

def rotate_and_scale(contour, angle:float=0., centre:Optional[Union[Tuple, List, np.ndarray]]=None, scalefactor=1.):
    """
    Rotates and/or scales a contour around a center **centre**.

    :param contour: shape (2, N)
    :param angle: angle, in radians
    :param centre: coordinates (x, y), in px
    :param scalefactor:
    :return:
    """
    if centre is None: # centre of rotation
        centre = (0, 0)
    rot_mat = getrotationandscalematrix(centre, angle=angle, scalefactor=scalefactor)
    x_rotated = rot_mat[0,0] * contour[0] + rot_mat[0, 1] * contour[1] + rot_mat[0, 2]
    y_rotated = rot_mat[1,0] * contour[0] + rot_mat[1, 1] * contour[1] + rot_mat[1, 2]
    return x_rotated, y_rotated

def estimate_parameters(image:np.ndarray, contour:np.ndarray, px_per_mm) -> Parameters:
    """Provides a coarse estimation of the parameters using (hopefully) robust techniques.

    Parameters
    ----------
    image : ndarray
        The image of the drop
    contour : ndarray
        The contour of the drop, with shape (2, N)
    px_per_mm : float
        The pixel density of the image.

    Returns
    -------
    parameters: Parameters
        An estimation of the parameters describing the drop.

    """
    if image.shape == (2,): # for old code compatibility # depreciate #todo remove this one day
        centre_of_image = image
    else:
        centre_of_image = image_centre(image)

    ### ANGLE OF GRAVITY
    gravity_angle:float = 0.
    try:
        slope, intercept = np.polyfit(contour[1], contour[0], deg=1)
        abc0 = np.array([slope, -1., intercept])
        # abc0 = np.array([0., -1., contour[0].mean()])

        def dist(abc, contour:np.ndarray) -> float:
            return np.sum((abc[0]*contour[1] + abc[1]*contour[0] +abc[2])**2/(abc[0]**2+abc[1]**2))


        bestline = minimize(dist, abc0, args=(contour))
        a, b, c = bestline.x


        gravity_angle = np.arctan(-a/b)
        # we do a trick to have the angle between -90 and 90 deg
        gravity_angle = (np.pi/2 + np.arctan2(-a, b))%(np.pi) - np.pi/2

        if (np.abs(gravity_angle*180/np.pi) > 15):
            warning(f'WARN: the angle of gravity was detected to {round(gravity_angle*180/np.pi, 2)} deg.')
            warning(f'WARN: This is likely an error so I put it back to {gravity_angle}.')
            gravity_angle = 0
    except:
        warning(f"WARN: couldn't get gravity angle. Falling back to {gravity_angle}")

    trace(f"\tFound gravity_angle={gravity_angle*180/np.pi} deg")

    # Now we need to rotate the contour in order to correctly estimate the other parameters
    contour_tiltcorrected = rotate_and_scale(contour, angle=-gravity_angle, centre=centre_of_image)

    ### Position of the tip

    # we guess it from the tilt-corrected contour
    y_tip_position_tiltcorrected = contour_tiltcorrected[1].max()
    x_tip_position_tiltcorrected = np.mean(contour_tiltcorrected[0][np.argmax(contour_tiltcorrected[1])])

    # we translate that to the real contour
    x_tip_position, y_tip_position = rotate_and_scale([x_tip_position_tiltcorrected, y_tip_position_tiltcorrected],
                                                      angle=gravity_angle, centre=centre_of_image)

    trace(f"\tFound x_tip_position={x_tip_position} px")
    trace(f"\tFound y_tip_position={y_tip_position} px")

    ### Radius of curvature
    De = contour_tiltcorrected[0].max() - contour_tiltcorrected[0].min()

    right = contour_tiltcorrected[0] > x_tip_position_tiltcorrected
    left = np.bitwise_not(right)
    Ds_height = y_tip_position_tiltcorrected - De
    x_ds_r = contour_tiltcorrected[0][right][np.argmin((contour_tiltcorrected[1][right] - Ds_height)**2)]
    x_ds_l = contour_tiltcorrected[0][left][np.argmin((contour_tiltcorrected[1][left] - Ds_height)**2)]
    Ds = x_ds_r - x_ds_l

    # Method 1: coarse estimate : max radius of the drop
    r0_px_coarse = De / 2
    # Method 2 : using the ugly formulas
    sigma = De/Ds
    bond = 0.12836 - 0.7577*sigma + 1.7713*sigma**2 - 0.5426*sigma**3
    ratio = 0.9987 + 0.1971 * bond - 0.0734 * bond**2 + 0.34708*bond**3
    r0_px_fine = De / (2 * ratio)

    # trace(f'De: {De} | Ds = {Ds}')
    # trace(f'sigma: {sigma} | bond2 = {bond}')

    # Method 3 : using a fit
    r0_px_fit = r0_px_coarse
    try:
        # finer estimation : we take the points near the tip (at a distance < r0_estimation_radius, in px) and do a 2nd order polynomial fitparams_handpicked
        r0_estimation_radius = r0_px_coarse/4 # this is tipNeighbourhood is pendent drop
        nearthetip = (contour_tiltcorrected[0] - x_tip_position_tiltcorrected)**2 + (contour_tiltcorrected[1] - y_tip_position_tiltcorrected)**2 < r0_estimation_radius**2
        x_contour_neartip = contour_tiltcorrected[0][nearthetip]
        y_contour_neartip  = contour_tiltcorrected[1][nearthetip]
        curvature_px = np.polyfit(x_contour_neartip, y_contour_neartip, 2)[0]
        r0_px_fit = np.abs(1/curvature_px)/2
    except:
        debug('Fit failed')

    # trace(f"\tr0= {round(r0_px_coarse, 2)} px [coarse] / {round(r0_px_fine, 2)} px [fine] / {round(r0_px_fit, 2)} px [fit] ")
    trace(f"\tr0= {round(r0_px_coarse/px_per_mm, 2)} mm [coarse] / {round(r0_px_fine/px_per_mm, 2)} mm [fine] / {round(r0_px_fit/px_per_mm, 2)} mm [fit] ")

    # lcap_px_coarse = np.sqrt(r0_px_coarse**2 / bond)
    # lcap_px_fine = np.sqrt(r0_px_fine**2 / bond)
    # lcap_px_fit = np.sqrt(r0_px_fit**2 / bond)
    # trace(f"\tlcap= {round(lcap_px_coarse/px_per_mm, 2)} mm [coarse] / {round(lcap_px_fine/px_per_mm, 2)} mm [fine] / {round(lcap_px_fit/px_per_mm, 2)} mm [fit] ")

    lcap_px_clueless:float = 2.7*px_per_mm # clueless guess : the fluid is pure water
    lcap_px = lcap_px_clueless

    params_estimated = Parameters()
    params_estimated.set_px_density(px_per_mm)
    params_estimated.set_a_rad(gravity_angle)
    params_estimated.set_x_px(x_tip_position)
    params_estimated.set_y_px(y_tip_position)
    params_estimated.set_r_px(r0_px_fit)
    params_estimated.set_l_px(lcap_px)

    params_estimated.describe(printfn=trace, descriptor='(estimated)')
    debug(f'Difference between contour and estimated profile: {round(compute_gap_pixel(contour, params_estimated), 2)} px^2')

    return params_estimated

### profile computing

def deriv(s_, rpkz):
    """
    The derivative along the arc of the variables.

    :param s_: (unused) The integration coordinate, the dimensionless arclength s
    :param rpkz: 4-array : [R, Psi, Kappa=dpsi/ds, Z]
    :return:
    """
    c = math.cos(rpkz[1])
    s = math.sin(rpkz[1])
    oneoverr = 1/rpkz[0]
    return [c, rpkz[2], -s + c * (s*oneoverr - rpkz[2])*oneoverr, s]

def greater_possible_zMax(tipRadius:float) -> float:
    """
    The max value zmax can take, from Daerr, pendent drop.

    :param tipRadius:
    :return:
    """
    return min(3.5, 3 / tipRadius) if tipRadius > .5 else 2 * tipRadius * (1 + 1.55*tipRadius)

def compute_nondimensional_profile(tipRadius:float, ds:float = 1e-3, approxLimit:float = 0.2, zMax:float = None) -> Tuple[np.ndarray, np.ndarray]:
    """Computes the nondimensional profile, starting at the bottom and up to an height zMax.

    About the default value of ds:
    The length in px of the contour is L. We want around 2 points per pixel, and the length of the dimensionless drop will be
    s = L / (px_per_mm * capillarylength_in_mm).
    Thus taking a typical 100 px/mm (microscopic resolution is 1000) and a capillary length of 2.5, we have
    ds = s / (2 * L) = 1 / (2 * 100 * 2.5) = 2e-3
    To be safe, we take ds = 1e-3 by default.
    If using high resolution camera + excellent optics + optimal conditions, one might want it smaller.

    About the solver : We use LSODA form LAPACK (scipy.integrate's odeint). Good ol' Fortran never dissapoints.

    Parameters
    ----------
    tipRadius : float, optional
        The dimensionless tip radius r_0/l_c (square root of the Bond number).
    ds : float, optional
        The dimensionless integration step. The default value (1e-3) should be enough for most applications.
    approxLimit : float, optional
        The fraction of capillary length or tip radius (whichever is smaller) up to which we use the approximate solution.
        todo: compute the difference between "true" profile (approxLimit = 1e-3) and the others to see what is the maximum reasonable approxlimit.
    zMax : float, optional
        The maximum height of the drop [useless]

    Returns
    -------
    R, Z : Tuple[ndarray]
        The right (R > 0) half of the dimensionless profile of the drop.

    """
    if zMax is None:
        zMax = greater_possible_zMax(tipRadius)

    ### NEAR THE TIP (singularity handling by asymptotic development)

    # curvilinear coordinate where we switch from the approximate solution to integration
    sLimit = approxLimit * min(1., tipRadius) # sLimit << (Cap length, Tip radisu)

    # the curvilinear coordinates we will use
    s_neartip = np.arange(0, sLimit, ds, dtype=float)

    RPKZ_neartip = np.empty((len(s_neartip), 4))

    # use the approximation near the tip
    RPKZ_neartip[:, 0] = tipRadius * np.sin(s_neartip/tipRadius) + s_neartip**5/(40*tipRadius**2)
    RPKZ_neartip[:, 1] = s_neartip * (1 - s_neartip**2 / 8) / tipRadius
    RPKZ_neartip[:, 2] = (1 - 3 * s_neartip**2 / 8) / tipRadius
    RPKZ_neartip[:, 3] = s_neartip**2 * ( 1 + (1/16 - 1/(12*tipRadius**2)) * s_neartip**2 ) / (2*tipRadius)

    # AWAY FROM THE TIP
    N_awayfromtip = int(5 / ds)+1
    s_awayfromtip = np.arange(N_awayfromtip) * ds + s_neartip[-1]

    RPKZ_initial = RPKZ_neartip[-1, :]

    RPKZ_awayfromtip:np.ndarray = odeint(deriv, RPKZ_initial, s_awayfromtip, tfirst=True)
    # # if anyone wants to use RK45 explicitely (works but slower because the new and shiny solve_ivp is slower than the good ol' odeint):
    # RPKZ_awayfromtip = solve_ivp(deriv, [s_awayfromtip[0], s_awayfromtip[-1]], RPKZ_initial, method='RK45', t_eval=s_awayfromtip)
    # RPKZ_awayfromtip = RPKZ_awayfromtip.T

    Nmax_zMax_attained = N_awayfromtip if RPKZ_awayfromtip[-1, 3] <= zMax else np.argmax(RPKZ_awayfromtip[:, 3] > zMax)
    Nmax_axisymmetry = N_awayfromtip if RPKZ_awayfromtip[:, 0].min() > 0 else np.argmax(RPKZ_awayfromtip[:, 0] <= 0)
    Nmax_goingup = N_awayfromtip if RPKZ_awayfromtip[:, 1].min() > 0 else np.argmax(RPKZ_awayfromtip[:, 1] <= 0)
    Nmax_neck = np.argmin(np.maximum( RPKZ_awayfromtip[1:,1] > np.pi/2 , RPKZ_awayfromtip[:-1,1] <= np.pi/2))
    if Nmax_neck == 0: Nmax_neck = N_awayfromtip

    RPKZ_awayfromtip = RPKZ_awayfromtip[:min(Nmax_zMax_attained, Nmax_axisymmetry, Nmax_goingup, Nmax_neck),:]

    # combine everything
    RPKZ = np.concatenate((RPKZ_neartip, RPKZ_awayfromtip), axis=0)

    return RPKZ[:, 0], RPKZ[:, 3]

def integrated_contour(parameters:Parameters) -> np.ndarray:
    """The computed profile in pixel coordinates.

    Parameters
    ----------
    parameters : Parameters

    Returns
    -------
    contour: Tuple[ndarray, ndarray]
        The computed profile in pixel coordinates (shape 2, N).

    """

    tipRadius = parameters.get_dimensionlessTipRadius()
    x_tip_position, y_tip_position = parameters.get_xy_px()
    gravity_angle = parameters.get_a_rad()
    caplength_px = parameters.get_l_px()

    # hence the profile
    R, Z = compute_nondimensional_profile(tipRadius)

    # FOR DISPLAY : WE MAKE Rdim AND Zdim, TO SHOW ON IMAGE

    # we scale, then rotate (these two can be exchanged), then move
    Rdim, Zdim = R.copy(), Z.copy()

    # complete, using axisymmetry
    Rdim = np.concatenate((-Rdim[::-1], Rdim))
    Zdim = np.concatenate(( Zdim[::-1], Zdim))

    # Reverse Z because we have this weird image coordinated system
    Zdim *= -1
    # scaling (first by capillary length to dimensionalize, then by pizel size to fit the image)
    # rotate, around the tip at (0,0)
    Rdim, Zdim = rotate_and_scale([Rdim, Zdim], angle=gravity_angle, scalefactor=caplength_px)

    # moving
    Rdim = Rdim + x_tip_position
    Zdim = Zdim + y_tip_position

    return np.array((Rdim, Zdim))

#compare computed profile to real profile
def compute_gap_dimensionless(contour:np.ndarray, parameters:Parameters) -> float:
    """The dimensionless area between the detected contour and the computed profile.

    Parameters
    ----------
    contour : ndarray
        The pixel coordinates of the detected contour to be compared with the computed profile, shape=(2, N)
    parameters : Parameters
        The parameters to compute the theoretical profile.

    Returns
    -------
    gap_dimensionless : float

    """
    fitparams:Fitparams = parameters.get_fitparams()

    return compute_gap_dimensionless_fromfitparams(fitparams=fitparams, contour=contour)
def compute_gap_pixel(contour:np.ndarray, parameters:Parameters) -> float:
    """The area between the detected contour and the computed profile, in squared pixels.

    Parameters
    ----------
    contour : ndarray
        The pixel coordinates of the detected contour to be compared with the computed profile, shape=(2, N)
    parameters : Parameters
        The parameters to compute the theoretical profile.

    Returns
    -------
    gap_in_squared_px : float

    """
    l_px = parameters.get_l_px()

    return compute_gap_dimensionless(contour, parameters)**(2/3) * l_px**2
def compute_gap_dimensionless_fromfitparams(fitparams:Fitparams, contour) -> float:
    gravity_angle, x_tip_position, y_tip_position, r0_px, capillary_length_px = fitparams

    tipRadius = r0_px / capillary_length_px

    # hence the profile
    R, Z = compute_nondimensional_profile(tipRadius)

    # FOR COMPUTE THE DIFF : we take it backward
    XY = contour.copy()

    #moving
    XY[0] -= x_tip_position
    XY[1] -= y_tip_position

    #  rotating and scaling
    XY = rotate_and_scale(XY, angle=-gravity_angle, scalefactor=-1 / capillary_length_px)

    # # cutting off :
    # XY = np.take(XY, np.where(XY[1] < Z.max())[0], axis=1)


    # separating the two sides
    rightside = XY[0] > 0
    X1, Y1 = np.take(XY, np.where(rightside)[0], axis=1)
    # X2, Y2 = -X[X < 0], Y[X < 0]
    # X2, Y2 = XY[:, np.bitwise_not(rightside)
    X2, Y2 = np.take(XY, np.where(np.bitwise_not(rightside))[0], axis=1)
    X2 *= -1

    # the differences
    R1 = np.interp(Y1, Z, R) # the radius corresponding to the side 1
    R2 = np.interp(Y2, Z, R) # the radius corresponding to the side 2

    R1[Y1 > Z.max()] = R[np.argmax(Z)]
    R2[Y2 > Z.max()] = R[np.argmax(Z)]

    R1[Y1 < Z.min()] *= 0
    R2[Y2 < Z.min()] *= 0
    DX1 = X1 - R1
    DX2 = X2 - R2

    difference = np.abs(trapezoid(DX1**2, Y1)) + np.abs(trapezoid(DX2**2, Y2))
    return difference

# compute the optimal profile
def optimize_profile(contour:np.ndarray, parameters_initialguess:Parameters,
                     to_fit:Optional[List[bool]]=None,
                     maxiter:Optional[int]=None, method:Optional[str]=None) -> Tuple[bool, Parameters]:
    """Computes the optimized parameters for the given ``contour``.

    Minimises the :func:`dimensionless gap <pypendentdrop.compute_gap_dimensionless>` between the contour and the computed profile,
    using scipy's ``minimize``.

    Parameters
    ----------
    contour : ndarray
        The pixel coordinates of the detected contour to be compared with the computed profile, shape=(2, N)
    parameters_initialguess : Parameters
        The initial guess of the parameters
    to_fit : Tuple[bool, bool, bool, bool, bool], optional
        Whether of not to fit the parameters todo: better document this (SEE EXAMPLES)
    maxiter : int, optional
        The maximum number of iterations. Depends on the method !
    method : str, optional
        The method passed to ``minimize``. Must be a bound-constrained method. Nelder-Mead works quite well.

    Returns
    -------

    """
    if method is None:
        method = 'Nelder-Mead'
    if to_fit is None:
        to_fit = [True, True, True, True, True]
    if maxiter is None:
        if method == 'Powell':
            maxiter = 100
        elif method == 'Nelder-Mead':
            maxiter = 2000 # should not take long

    default_bounds = [(None, None),  # gravity_angle
                      (None, None),  # y_tip_position
                      (None, None),  # x_tip_position
                      (0, None),  # r0_mm
                      (0, None)] # capillary length (mm)

    fitparams_initial = parameters_initialguess.get_fitparams()

    bounds = [default_bounds[i] if to_fit[i] else (fitparams_initial[i], fitparams_initial[i]) for i in range(len(fitparams_initial))]

    # we remove the top 5 pixels, i.e. the points too close to the top edge
    # gravity_angle = parameters_initialguess.get_a_rad()
    nottooclosefromthetop = contour[1]-contour[1].min() > 5/np.cos(parameters_initialguess.get_a_rad())
    contour_opti = contour[:, nottooclosefromthetop]

    options={}
    if maxiter is not None:
        options['maxiter'] = maxiter

    # pendent drop uses Powell's method with maxiter = 100 (typically maxiter = 10),
    # but I found the Nelder-Mead algorithm to be 25% faster ?
    # for method = Nelder-Mead, options={'adaptive':False, 'disp':False}
    trace(f'Fitparams initial: {[round(fpi, 5) for fpi in fitparams_initial]}')
    trace(f'Bounds: {bounds}')
    trace(f'Contour shape: {contour.shape} (min-max = {contour.min()}-{contour.max()})')
    trace(f'Optimization: {method} method (options: {options})')

    t1 = time.time()
    minimization = minimize(compute_gap_dimensionless_fromfitparams, x0=np.array(fitparams_initial), args=(contour_opti),
                            bounds=bounds, method=method, options=options)
    t2 = time.time()
    debug(f'optimize_profile: Optimisation time: {int((t2-t1)*1000)} ms')

    optimization_success = minimization.success

    debug(f'optimize_profile: {minimization.nit} iterations, {minimization.nfev} calls to function')
    trace(f'optimize_profile: Minimization message: {minimization.message}')

    if not(minimization.success):
        info('Minimizaton failed')
        debug(f'Minimization unsuccessful: {minimization.message}')
        return False, parameters_initialguess


    # copy `by hand'
    # todo implement a copy method for the Parameters class and use it here
    parameters_opti = Parameters()
    parameters_opti.set_px_density(parameters_initialguess.get_px_density())
    parameters_opti.set_g(parameters_initialguess.get_g())
    parameters_opti.set_d(parameters_initialguess.get_d())
    # update with the optimized values
    parameters_opti.set_a_rad(minimization.x[0])
    parameters_opti.set_x_px(minimization.x[1])
    parameters_opti.set_y_px(minimization.x[2])
    parameters_opti.set_r_px(minimization.x[3])
    parameters_opti.set_l_px(minimization.x[4])

    parameters_opti.describe(printfn=trace, descriptor='(optimized)')
    debug(f'Difference between contour and optimized profile: {round(compute_gap_pixel(contour, parameters_opti), 2)} px^2')

    return True, parameters_opti
