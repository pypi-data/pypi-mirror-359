API Reference
========================

On this page:

`Image import`_

`Contour detection`_

`Parameters estimation`_

`Parameters optimization`_

`Plotting`_


Image import
--------------------

Import images using :func:`import_image <pypendentdrop.import_image>`, which is good-mannered enough to tell you if the import succeeded and to provide you an image even in case of failure, which can be practical.

.. autofunction:: pypendentdrop.import_image

Contour detection
--------------------

The detection of a drop contour is made by

1. Selecting a threshold value for the luminosity (manually or using :func:`auto_threshold <pypendentdrop.auto_threshold>`), and
2. Finding the main contour (the one of the drop) using :func:`detect_main_contour <pypendentdrop.detect_main_contour>`.

.. autofunction:: pypendentdrop.auto_threshold

.. autofunction:: pypendentdrop.detect_main_contour

.. autofunction:: pypendentdrop.detect_contourlines

The drop parameters
-----------------------

One has to provide a reasonable estimation of the parameters describing the drop (angle of gravity, tip position, apex radius of curvature, capillary length) as initial condition for the optimization to converge to a relevant minimum in the parameters space.

All the drops parameters are handled using a Parameter object. An automatic estimation of these parameters can be obtained by using :func:`estimate_parameters <pypendentdrop.estimate_parameters>` and later modified using the methods of the Parameters class.

.. autofunction:: pypendentdrop.estimate_parameters

.. autoclass:: pypendentdrop.Parameters
   :members:

..    comment
    .. automethod:: describe_acquisition
    .. automethod:: get_bond

Optimization
------------------------

Using :func:`optimize_profile <pypendentdrop.optimize_profile>`, one can find the parameters that fits best a given detected contour (in pixel coordinates). The contour is numerically integrated using :func:`compute_nondimensional_profile <pypendentdrop.compute_nondimensional_profile>`, and compared with the detected profile using :func:`compute_gap_dimensionless <pypendentdrop.compute_gap_dimensionless>`. The parameters are then varied to minimize the dimensionless total area of the gap between the two. This area between them can be computed in real-world units (squared pixels) using :func:`compute_gap_pixel <pypendentdrop.compute_gap_pixel>`. In order to plot the theoretical profile, :func:`integrated_contour <integrated_contour.integrated_contour>` allows one to obtain the contour integrated from the equations in pixel coordinates.

.. autofunction:: pypendentdrop.compute_nondimensional_profile

.. autofunction:: pypendentdrop.compute_gap_dimensionless

.. autofunction:: pypendentdrop.compute_gap_pixel

.. autofunction:: pypendentdrop.optimize_profile

.. autofunction:: pypendentdrop.integrated_contour

Plotting
--------------------

TODO