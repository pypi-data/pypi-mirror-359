"""
Photometric package
===================

Defines a Filter class and associated functions to extract photometry.

This also include functions to keep libraries up to date

.. note::

    integrations are done using :func:`trapezoid`
    Why not Simpsons? Simpsons principle is to take sequence of 3 points to
    make a quadratic interpolation. Which in the end, when filters have sharp
    edges, the error due to this "interpolation" are extremely large in
    comparison to the uncertainties induced by trapeze integration.
"""
from __future__ import print_function, division
import numpy as np
import tables

try:
    from scipy.integrate import trapezoid
except ImportError:  # older scipy / numpy < 2.0
    from scipy.integrate import trapz as trapezoid
    
from functools import wraps

from .simpletable import SimpleTable
from .ezunits import hasUnit, unit
from .vega import Vega
from .config import libsdir

import os

# directories
__default__ = libsdir.joinpath('new_filters.hd5')


class Constants(object):
    """ A namespace for constants """
    # Planck's constant in erg * sec
    h = 6.626075540e-27 * unit['erg * s']
    # Speed of light in cm/s
    # c = 2.99792458e18 * unit['AA / s']
    c = unit['c'].to('AA/s')


class set_method_default_units(object):
    """ Decorator for classmethods that makes sure that
    the inputs of slamb, sflux are in given units

    expects the decorated method to be defined as
        >> def methodname(self, lamb, flux)
    """

    def __init__(self, wavelength_unit, flux_unit, output_unit=None):
        self.wavelength_unit = unit[wavelength_unit]
        self.flux_unit = unit[flux_unit]
        self.output_unit = output_unit

    @classmethod
    def force_units(cls, value, unit):
        if unit is None:
            return value
        try:
            return value.to(unit)
        except AttributeError:
            print('Warning: assuming {0:s} units to unitless object.'.format(str(unit)))
            return value * unit

    def __call__(self, func):

        @wraps(func)
        def wrapper(filter_, slamb, sflux, *args, **kwargs):
            _slamb = set_method_default_units.force_units(slamb, self.wavelength_unit)
            _sflux = set_method_default_units.force_units(sflux, self.flux_unit)
            output = func(filter_, _slamb, _sflux, *args, **kwargs)
            return set_method_default_units.force_units(output, self.output_unit)

        return wrapper


def _drop_units(q):
    """ Drop the unit definition silently """
    try:
        return q.magnitude
    except AttributeError:
        return q


class Filter(object):
    """Class filter

    Define a filter by its name, wavelength and transmission
    The type of detector (energy or photon counter) can be specified for
    adapting calculations. (default: photon)

    Attributes
    ----------
    name: str
        name of the filter

    norm: float
        normalization factor of the filter

    transmit: ndarray
        transmission curve of the filter

    dtype: str
        detector type, either "photon" or "energy" counter

    unit: str
        wavelength units
    """
    def __init__(self, wavelength, transmit, name='', dtype="photon", unit=None):
        """Constructor"""
        self.name       = name
        self.set_dtype(dtype)
        try:   # get units from the inputs
            self._wavelength = wavelength.magnitude
            unit = str(wavelength.units)
        except AttributeError:
            self._wavelength = wavelength
        self.set_wavelength_unit(unit)
        
        # make sure input data are ordered and cleaned of weird values.
        idx = np.argsort(self._wavelength)
        self._wavelength = self._wavelength[idx]        
        self.transmit   = np.clip(transmit[idx], 0., np.nanmax(transmit))
        
        self.norm       = trapezoid(self.transmit, self._wavelength)
        self._lT        = trapezoid(self._wavelength * self.transmit, self._wavelength)
        self._lpivot    = self._calculate_lpivot()
        self._cl        = self._lT / self.norm

    def _calculate_lpivot(self):
        if 'photon' in self.dtype:
            lpivot2 = self._lT / trapezoid(self.transmit / self._wavelength, self._wavelength)
        else:
            lpivot2 = self.norm / trapezoid(self.transmit / self._wavelength ** 2, self._wavelength)
        return np.sqrt(lpivot2)

    def set_wavelength_unit(self, unit):
        """ Set the wavelength units """
        try:   # get units from the inputs
            self.wavelength_unit = str(self._wavelength.units)
        except AttributeError:
            self.wavelength_unit = unit

    def set_dtype(self, dtype):
        """ Set the detector type (photon or energy)"""
        _d = dtype.lower()
        if "phot" in _d:
            self.dtype = "photon"
        elif "ener" in _d:
            self.dtype = "energy"
        else:
            raise ValueError('Unknown detector type {0}'.format(dtype))

    def info(self, show_zeropoints=True):
        """ display information about the current filter"""
        print("""Filter object information:
    name:                 {s.name:s}
    detector type:        {s.dtype:s}
    wavelength units:     {s.wavelength_unit}
    central wavelength:   {s.cl:f}
    pivot wavelength:     {s.lpivot:f}
    effective wavelength: {s.leff:f}
    photon wavelength:    {s.lphot:f}
    minimum wavelength:   {s.lmin:f}
    maximum wavelength:   {s.lmax:f}
    norm:                 {s.norm:f}
    effective width:      {s.width:f}
    fullwidth half-max:   {s.fwhm:f}
    definition contains {s.transmit.size:d} points""".format(s=self).replace('None', 'unknown'))

        # zero points only if units
        if (self.wavelength_unit is None) or (not show_zeropoints):
            return

        print("""
    Zeropoints
        Vega: {s.Vega_zero_mag:f} mag,
              {s.Vega_zero_flux},
              {s.Vega_zero_Jy}
              {s.Vega_zero_photons}
          AB: {s.AB_zero_mag:f} mag,
              {s.AB_zero_flux},
              {s.AB_zero_Jy}
          ST: {s.ST_zero_mag:f} mag,
              {s.ST_zero_flux},
              {s.ST_zero_Jy}
        """.format(s=self))

    def __repr__(self):
        return "Filter: {0:s}, {1:s}".format(self.name, object.__repr__(self))

    @property
    def wavelength(self):
        """ Unitwise wavelength definition """
        if self.wavelength_unit is not None:
            return self._wavelength * unit[self.wavelength_unit]
        else:
            return self._wavelength

    @property
    def lmax(self):
        """ Calculated as the last value with a transmission at least 1% of
        maximum transmission """
        return max(self.wavelength[(self.transmit / self.transmit.max()) > 1./100])

    @property
    def lmin(self):
        """ Calculate das the first value with a transmission at least 1% of
        maximum transmission """
        return min(self.wavelength[(self.transmit / self.transmit.max()) > 1./100])

    @property
    def width(self):
        """ Effective width
        Equivalent to the horizontal size of a rectangle with height equal
        to maximum transmission and with the same area that the one covered by
        the filter transmission curve.

        W = int(T dlamb) / max(T)
        """
        return (self.norm / max(self.transmit)) * unit[self.wavelength_unit]

    @property
    def fwhm(self):
        """ the difference between the two wavelengths for which filter
        transmission is half maximum

        ..note::
            This calculation is not exact but rounded to the nearest passband
            data points
        """
        vals = self.transmit / self.transmit.max() - 0.5
        zero_crossings = np.where(np.diff(np.sign(vals)))[0]
        lambs = self.wavelength[zero_crossings]
        return np.diff(lambs)[0] * unit[self.wavelength_unit]

    @property
    def lpivot(self):
        """ Unitwise wavelength definition """
        if self.wavelength_unit is not None:
            return self._lpivot * unit[self.wavelength_unit]
        else:
            return self._lpivot

    @property
    def cl(self):
        """ Unitwise wavelength definition """
        if self.wavelength_unit is not None:
            return self._cl * unit[self.wavelength_unit]
        else:
            return self._cl

    @property
    def leff(self):
        """ Unitwise Effective wavelength
        leff = int (lamb * T * Vega dlamb) / int(T * Vega dlamb)
        """
        with Vega() as v:
            s = self.reinterp(v.wavelength)
            w = s._wavelength
            leff = np.trapz(w * s.transmit * v.flux.magnitude, w, axis=-1)
            leff /= np.trapz(s.transmit * v.flux.magnitude, w, axis=-1)
        if self.wavelength_unit is not None:
            return leff * unit[self.wavelength_unit]
        else:
            return leff

    @property
    def lphot(self):
        """ Photon distribution based effective wavelength. Defined as

        lphot = int(lamb ** 2 * T * Vega dlamb) / int(lamb * T * Vega dlamb)

        which we calculate as

        lphot = get_flux(lamb * vega) / get_flux(vega)
        """
        if self.wavelength_unit is None:
            raise AttributeError('Needs wavelength units')

        with Vega() as v:
            f_vega = self.get_flux(v.wavelength, v.flux.magnitude, axis=-1)
            f_lamb_vega = self.get_flux(v.wavelength, v.wavelength * v.flux.magnitude, axis=-1)
            f_lamb2_vega = self.get_flux(v.wavelength, v.wavelength ** 2 * v.flux.magnitude, axis=-1)
        if 'photon' in self.dtype:
            lphot = (f_lamb_vega / f_vega)
        else:
            lphot = f_lamb2_vega / f_lamb_vega
        return lphot * unit[self.wavelength_unit]

    def _get_filter_in_units_of(self, slamb=None):
        w = self.wavelength
        if hasUnit(slamb) & hasUnit(w):
            return w.to(str(slamb.units)).magnitude
        else:
            print("Warning: assuming units are consistent")
            return self._wavelength

    def get_Nphotons(self, slamb, sflux, axis=-1):
        """getNphot the number of photons through the filter
        (Ntot / width  in the documentation)

        getflux() * leff / hc

        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain

        sflux: ndarray(dtype=float, ndim=1)
            associated flux in erg/s/cm2/AA

        Returns
        -------
        N: float
            Number of photons of the spectrum within the filter
        """
        passb = self.reinterp(slamb)
        wave = passb._wavelength
        dlambda = np.diff(wave)

        # h = 6.626075540e-27    # erg * s
        # c = 2.99792458e18      # AA / s
        h = Constants.h.to('erg * s').magnitude
        c = Constants.c.to('AA/s').magnitude
        vals = passb.transmit * _drop_units(sflux) * wave
        vals[~np.isfinite(vals)] = 0.
        Nphot = 0.5 * np.sum((vals[1:] + vals[:-1]) * dlambda) / (h * c)
        Nphot = Nphot * unit['photon/s/cm**2']

        return Nphot / passb.width   # photons / cm2 / s / A

    @property
    def Vega_zero_photons(self):
        """ Vega number of photons per wavelength unit

        .. note::

            see `self.get_Nphotons`
        """
        with Vega() as v:
            return self.get_Nphotons(v.wavelength, v.flux)

    def getFlux(self, slamb, sflux, axis=-1):
        """getFlux
        Integrate the flux within the filter and return the integrated energy
        If you consider applying the filter to many spectra, you might want to
        consider extractSEDs.

        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain

        sflux: ndarray(dtype=float, ndim=1)
            associated flux

        Returns
        -------
        flux: float
            Energy of the spectrum within the filter
        """
        _wavelength = self._get_filter_in_units_of(slamb)
        _slamb = _drop_units(slamb)
        #clean data for inf values by interpolation
        if True in np.isinf(sflux):
            indinf = np.where(np.isinf(sflux))
            indfin = np.where(np.isfinite(sflux))
            sflux[indinf] = np.interp(_slamb[indinf], _slamb[indfin], sflux[indfin])

        # reinterpolate transmission onto the same wavelength def as the data
        ifT = np.interp(_slamb, _wavelength, self.transmit, left=0., right=0.)

        # if the filter is null on that wavelength range flux is then 0
        # ind = ifT > 0.
        nonzero = np.where(ifT > 0)[0]
        if nonzero.size <= 0:
            return 0.
        nonzero_start = max(0, min(nonzero) - 5)
        nonzero_end = min(len(ifT), max(nonzero) + 5)
        ind = np.zeros(len(ifT), dtype=bool)
        ind[nonzero_start:nonzero_end] = True
        if True in ind:
            try:
                _sflux = sflux[:, ind]
            except Exception:
                _sflux = sflux[ind]
            # limit integrals to where necessary
            # ind = ifT > 0.
            if 'photon' in self.dtype:
                a = np.trapz(_slamb[ind] * ifT[ind] * _sflux, _slamb[ind], axis=axis)
                b = np.trapz(_slamb[ind] * ifT[ind], _slamb[ind] )
            elif 'energy' in self.dtype:
                a = np.trapz( ifT[ind] * _sflux, _slamb[ind], axis=axis )
                b = np.trapz( ifT[ind], _slamb[ind])
            if (np.isinf(a).any() | np.isinf(b).any()):
                print(self.name, "Warn for inf value")
            return a / b
        else:
            return 0.

    def get_flux(self, slamb, sflux, axis=-1):
        """getFlux
        Integrate the flux within the filter and return the integrated energy
        If you consider applying the filter to many spectra, you might want to
        consider extractSEDs.

        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain

        sflux: ndarray(dtype=float, ndim=1)
            associated flux

        Returns
        -------
        flux: float
            Energy of the spectrum within the filter
        """
        return self.getFlux(slamb, sflux, axis=axis)

    def reinterp(self, lamb):
        """ reinterpolate filter onto a different wavelength definition """
        _wavelength = self._get_filter_in_units_of(lamb)
        _lamb = _drop_units(lamb)
        try:
            _unit = str(lamb.units)
        except AttributeError:
            _unit = self.wavelength_unit
        ifT = np.interp(_lamb, _wavelength, self.transmit, left=0., right=0.)
        return self.__class__(_lamb, ifT, name=self.name, dtype=self.dtype, unit=_unit)

    def __call__(self, slamb, sflux):
        return self.applyTo(slamb, sflux)

    def apply_transmission(self, slamb, sflux):
        """
        Apply filter transmission to a spectrum (with reinterpolation of the filter)

        Parameters
        ----------
        slamb: ndarray
            spectrum wavelength definition domain

        sflux: ndarray
            associated flux

        Returns
        -------
        flux: float
            new spectrum values accounting for the filter
        """
        _wavelength = self._get_filter_in_units_of(slamb)
        _lamb = _drop_units(slamb)
        ifT = np.interp(_lamb, _wavelength, self.transmit, left=0., right=0.)
        return ifT * sflux

    def applyTo(self, slamb, sflux):
        """ For compatibility but bad name """
        return self.apply_transmission(slamb, sflux)

    @classmethod
    def from_ascii(cls, fname, dtype='csv', **kwargs):
        """ Load filter from ascii file """
        lamb = kwargs.pop('lamb', None)
        name = kwargs.pop('name', None)
        detector = kwargs.pop('detector', 'photon')
        unit = kwargs.pop('unit', None)

        t = SimpleTable(fname, dtype=dtype, **kwargs)
        w = t['WAVELENGTH'].astype(float)
        r = t['THROUGHPUT'].astype(float)

        # update properties from file header
        detector = t.header.get('DETECTOR', detector)
        unit     = t.header.get('WAVELENGTH_UNIT', unit)
        name     = t.header.get('NAME', name)

        # try from the comments in the header first
        if name in (None, 'None', 'none', ''):
            name = [k.split()[1]
                    for k in t.header.get('COMMENT', '').split('\n')
                    if 'COMPNAME' in k]
            name = ''.join(name).replace('"','').replace("'",'')
        # if that did not work try the table header directly
        if name in (None, 'None', 'none', ''):
            name = t.header['NAME']

        _filter = Filter(w, r, name=name, dtype=detector, unit=unit)

        # reinterpolate if requested
        if lamb is not None:
            _filter = _filter.reinterp(lamb)

        return _filter

    def write_to(self, fname, **kwargs):
        """ Export filter to a file

        Parameters
        ----------
        fname: str
            filename

        Uses `SimpleTable.write` parameters
        """
        data = self.to_Table()
        data.write(fname, **kwargs)

    def to_Table(self, **kwargs):
        """ Export filter to a SimpleTable object

        Parameters
        ----------
        fname: str
            filename

        Uses `SimpleTable` parameters
        """
        data = SimpleTable({'WAVELENGTH': self._wavelength,
                            'THROUGHPUT': self.transmit})

        if self.wavelength_unit is not None:
            data.header['WAVELENGTH_UNIT'] = self.wavelength_unit
        data.header['DETECTOR'] = self.dtype
        data.header['COMPNAME'] = str(self.name)
        data.header['NAME'] = str(self.name)
        data.set_comment('THROUGHPUT', 'filter throughput definition')
        data.set_comment('WAVELENGTH', 'filter wavelength definition')
        data.set_comment('WAVELENGTH', self.wavelength_unit or 'AA')
        return data

    def to_dict(self):
        """ Return a dictionary of the filter """
        data = {'WAVELENGTH': self._wavelength, 'THROUGHPUT': self.transmit}
        if self.wavelength_unit is not None:
            data['WAVELENGTH_UNIT'] = self.wavelength_unit
        data['DETECTOR'] = self.dtype
        data['NAME'] = self.name
        data['PIVOT'] = self._lpivot
        data['CENTRAL'] = self._cl
        data['EFFECTIVE'] = _drop_units(self.leff)
        data['NORM'] = self.norm
        return data

    @classmethod
    def make_integration_filter(cls, lmin, lmax, name='', dtype='photon', unit=None):
        """ Generate an heavyside filter between lmin and lmax """
        dyn = lmax - lmin
        try:
            unit = str(dyn.units)
            dyn = _drop_units(dyn)
        except Exception:
            pass
        w = np.array([lmin - 0.01 * dyn, lmin, lmax, lmax + 0.01 * dyn])
        f = np.array([0., 1., 1., 0.])
        return Filter(w, f, name=name, dtype=dtype, unit=unit)

    @property
    def AB_zero_mag(self):
        """ AB magnitude zero point
        
        ABmag = -2.5 * log10(f_nu) - 48.60
              = -2.5 * log10(f_lamb) - 2.5 * log10(lpivot ** 2 / c) - 48.60
              = -2.5 * log10(f_lamb) - zpts

        """
        if self.wavelength_unit is None:
            raise AttributeError('Needs wavelength units')

        C1 = unit[self.wavelength_unit].to('AA').magnitude ** 2 / unit['c'].to('AA/s').magnitude
        c1 = self._lpivot ** 2 * C1

        m = 2.5 * np.log10(c1) + 48.6
        return m

    @property
    def AB_zero_flux(self):
        """ AB flux zero point in erg/s/cm2/AA """
        return 10 ** (-0.4 * self.AB_zero_mag) * unit['erg/s/cm ** 2/AA']

    @property
    def AB_zero_Jy(self):
        """ AB flux zero point in Jansky (Jy) """
        c = unit['1e-8 * c'].to('m/s').magnitude
        f = 1e5 / c * self.lpivot.magnitude ** 2 * self.AB_zero_flux.magnitude
        return f * unit['Jy']

    @property
    def Vega_zero_mag(self):
        """ vega magnitude zero point
        vegamag = -2.5 * log10(f_lamb) + 2.5 * log10(f_vega)
        vegamag = -2.5 * log10(f_lamb) - zpts
        """
        if self.wavelength_unit is None:
            raise AttributeError('Needs wavelength units')

        with Vega() as v:
            f_vega = self.get_flux(v.wavelength, v.flux.magnitude, axis=-1)
        return -2.5 * np.log10(f_vega)

    @property
    def Vega_zero_flux(self):
        """ Vega flux zero point in erg/s/cm2/AA """
        return 10 ** (-0.4 * self.Vega_zero_mag) * unit['erg/s/cm ** 2/AA']

    @property
    def Vega_zero_Jy(self):
        """ Vega flux zero point in Jansky (Jy) """
        c = unit['1e-8 * c'].to('m/s').magnitude
        f = 1e5 / c * self.lpivot.magnitude ** 2 * self.Vega_zero_flux.magnitude
        return f * unit['Jy']

    @property
    def ST_zero_mag(self):
        """ ST magnitude zero point
        STmag = -2.5 * log10(f_lamb) -21.1
        """
        return 21.1

    @property
    def ST_zero_flux(self):
        """ ST flux zero point in erg/s/cm2/AA """
        return 10 ** (-0.4 * self.ST_zero_mag) * unit['erg/s/cm ** 2/AA']

    @property
    def ST_zero_Jy(self):
        """ ST flux zero point in Jansky (Jy) """
        c = unit['1e-8 * c'].to('m/s').magnitude
        f = 1e5 / c * self.lpivot.magnitude ** 2 * self.ST_zero_flux.magnitude
        return f * unit['Jy']


class UncertainFilter(Filter):
    """ What could be a filter with uncertainties

    Attributes
    ----------
    mean: Filter
        mean passband transmission

    samples: sequence(Filter)
        samples from the uncertain passband transmission model

    name: string
        name of the passband

    dtype: str
        detector type, either "photon" or "energy" counter

    unit: str
        wavelength units
    """
    def __init__(self, wavelength, mean_transmit, samples,
                 name='', dtype='photon', unit=None):
        """ Constructor """
        self.mean_ = Filter(wavelength, mean_transmit,
                            name=name, dtype=dtype, unit=unit)
        self.samples_ = [Filter(wavelength, transmit_k,
                                name=name + '_{0:d}'.format(num),
                                dtype=dtype, unit=unit)
                         for (num, transmit_k) in enumerate(samples)]
        self.name = name
        self.dtype = self.mean_.dtype
        self.model_ = None

    @classmethod
    def from_gp_model(cls, model, xprime=None, n_samples=10, **kwargs):
        """ Generate a filter object from a sklearn GP model

        Parameters
        ----------
        model: sklearn.gaussian_process.GaussianProcessRegressor
            model of the passband
        xprime: ndarray
            wavelength to express the model in addition to the training points
        n_samples: int
            number of samples to generate from the model.
        kwawrgs: dict
            UncertainFilter keywords
        """
        if xprime is None:
            xpred = model.X_train_
        else:
            xpred = np.unique(np.hstack([_drop_units(xprime), model.X_train_.ravel()]))
            xpred = xpred.reshape(1, -1).T

        unit_ = kwargs.pop('unit', None)
        if unit_ is None:
            unit_ = str(getattr(xprime, 'units', None))

        mean_transmit, _ = model.predict(xpred, return_std=True)
        samples = model.sample_y(xpred, n_samples=n_samples)

        unc_filter = cls(xpred.ravel(),
                         mean_transmit,
                         samples.T, unit=unit_, **kwargs)

        unc_filter.model_ = model
        return unc_filter

    def info(self, show_zeropoints=True):
        """ display information about the current filter"""
        string = self.mean_.info(show_zeropoints)
        string = string.replace('Filter object information',
                                'Filter object mean information only')
        return string

    def set_dtype(self, dtype):
        """ Set the detector type (photon or energy)"""
        self.mean_.set_dtype(dtype)
        for filter_k in self.samples_:
            filter_k.set_dtype(dtype)
        self.dtype = self.mean_.dtype

    def set_wavelength_unit(self, unit):
        """ Set the wavelength units """
        self.mean_.set_wavelength_unit(unit)
        for filter_k in self.samples_:
            filter_k.set_wavelength_unit(unit)

    @property
    def wavelength(self):
        """ Unitwise wavelength definition """
        return self.mean_.wavelength

    @property
    def wavelength_unit(self):
        """ Unit wavelength definition """
        return self.mean_.wavelength_unit

    @property
    def _wavelength(self):
        """ Unitless wavelength definition """
        return self.mean_._wavelength

    @property
    def transmit(self):
        """ Transmission curves """
        return self._get_mean_and_samples_attribute('transmit')

    def _get_samples_attribute(self, attr, *args, **kwargs):
        """ Returns the attribute from all samples """
        try:
            vals = [getattr(fk, attr)(*args, **kwargs) for fk in self.samples_]
        except TypeError:
            vals = [getattr(fk, attr) for fk in self.samples_]
        try:
            unit_ = unit[str(vals[0].units)]
            return np.array([v.magnitude for v in vals]) * unit_
        except AttributeError:
            return np.array(vals)

    def _get_mean_attribute(self, attr, *args, **kwargs):
        """ Returns the attribute from the mean passband """
        attr = getattr(self.mean_, attr)
        try:
            return attr(*args, **kwargs)
        except TypeError:
            return attr

    def _get_mean_and_samples_attribute(self, attr, *args, **kwargs):
        """ Compute / extract mean and smapled filter attributes

        Parameters
        ----------
        attr: str
            attribute to get (can be a callable attribute)
        args: sequence
            any argument of attr
        kwargs: dict
            any keywords for attr

        Returns
        -------
        mean_: object
            value from the mean passband
        samples_: sequence(object)
            values from each sampled passband
        """
        return (self._get_mean_attribute(attr, *args, **kwargs),
                self._get_samples_attribute(attr, *args, **kwargs))

    @property
    def lmax(self):
        """ Calculated as the last value with a transmission at least 1% of
        maximum transmission """
        return self._get_mean_and_samples_attribute('lmax')

    @property
    def lmin(self):
        """ Calculate das the first value with a transmission at least 1% of
        maximum transmission """
        return self._get_mean_and_samples_attribute('lmin')

    @property
    def width(self):
        """ Effective width
        Equivalent to the horizontal size of a rectangle with height equal
        to maximum transmission and with the same area that the one covered by
        the filter transmission curve.

        W = int(T dlamb) / max(T)
        """
        return self._get_mean_and_samples_attribute('width')

    @property
    def fwhm(self):
        """ the difference between the two wavelengths for which filter
        transmission is half maximum

        ..note::
        
            This calculation is not exact but rounded to the nearest passband
            data points
        """
        return self._get_mean_and_samples_attribute('fwhm')

    @property
    def lpivot(self):
        """ Unitwise wavelength definition """
        return self._get_mean_and_samples_attribute('lpivot')


    @property
    def cl(self):
        """ Unitwise wavelength definition """
        return self._get_mean_and_samples_attribute('cl')

    @property
    def leff(self):
        """ Unitwise Effective wavelength
        leff = int (lamb * T * Vega dlamb) / int(T * Vega dlamb)
        """
        return self._get_mean_and_samples_attribute('leff')

    @property
    def lphot(self):
        """ Photon distribution based effective wavelength. Defined as

        lphot = int(lamb ** 2 * T * Vega dlamb) / int(lamb * T * Vega dlamb)

        which we calculate as

        lphot = get_flux(lamb * vega) / get_flux(vega)
        """
        return self._get_mean_and_samples_attribute('lphot')

    def get_Nphotons(self, slamb, sflux, axis=-1):
        """getNphot the number of photons through the filter
        (Ntot / width  in the documentation)

        getflux() * leff / hc

        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain

        sflux: ndarray(dtype=float, ndim=1)
            associated flux in erg/s/cm2/AA

        Returns
        -------
        N: float
            Number of photons of the spectrum within the filter
        """
        mean, samples = self._get_mean_and_samples_attribute('get_Nphotons',
                                                             slamb, sflux,
                                                             axis=axis)
        return mean, samples

    @property
    def Vega_zero_photons(self):
        """ Vega number of photons per wavelength unit

        .. note::

            see `self.get_Nphotons`
        """
        return self._get_mean_and_samples_attribute('Vega_zero_photons')

    def getFlux(self, slamb, sflux, axis=-1):
        """getFlux
        Integrate the flux within the filter and return the integrated energy
        If you consider applying the filter to many spectra, you might want to
        consider extractSEDs.

        Parameters
        ----------
        slamb: ndarray(dtype=float, ndim=1)
            spectrum wavelength definition domain

        sflux: ndarray(dtype=float, ndim=1)
            associated flux

        Returns
        -------
        flux: float
            Energy of the spectrum within the filter
        """
        mean, samples = self._get_mean_and_samples_attribute('getFlux',
                                                             slamb, sflux,
                                                             axis=axis)
        return mean, samples

    def reinterp(self, lamb):
        """ reinterpolate filter onto a different wavelength definition """
        mean, samples = self._get_mean_and_samples_attribute('reinterp')
        mean_val = mean(lamb)
        samp_val = [sk(mean_val.wavelength) for sk in samples]
        samp_transmissions = [sk.transmit for sk in samp_val]

        return self.__class__(mean_val.wavelength, mean_val.transmit,
                              samp_transmissions, name=self.name,
                              dtype=mean_val.dtype, unit=mean_val.wavelength_unit)

    def apply_transmission(self, slamb, sflux):
        """
        Apply filter transmission to a spectrum (with reinterpolation of the filter)

        Parameters
        ----------
        slamb: ndarray
            spectrum wavelength definition domain

        sflux: ndarray
            associated flux

        Returns
        -------
        flux: float
            new spectrum values accounting for the filter
        """
        mean, samples = self._get_mean_and_samples_attribute('apply_transmission')
        mean_val = mean(slamb, sflux)
        samp_val = [sk(slamb, sflux) for sk in samples]
        return mean_val, samp_val

    @property
    def AB_zero_mag(self):
        """ AB magnitude zero point

        ABmag = -2.5 * log10(f_nu) - 48.60
              = -2.5 * log10(f_lamb) - 2.5 * log10(lpivot ** 2 / c) - 48.60
              = -2.5 * log10(f_lamb) - zpts

        """
        return self._get_mean_and_samples_attribute('AB_zero_mag')

    @property
    def AB_zero_flux(self):
        """ AB flux zero point in erg/s/cm2/AA """
        return self._get_mean_and_samples_attribute('AB_zero_flux')

    @property
    def AB_zero_Jy(self):
        """ AB flux zero point in Jansky (Jy) """
        return self._get_mean_and_samples_attribute('AB_zero_Jy')

    @property
    def Vega_zero_mag(self):
        """ Vega magnitude zero point
        Vegamag = -2.5 * log10(f_lamb) + 2.5 * log10(f_vega)
        Vegamag = -2.5 * log10(f_lamb) - zpts
        """
        return self._get_mean_and_samples_attribute('Vega_zero_mag')

    @property
    def Vega_zero_flux(self):
        """ Vega flux zero point in erg/s/cm2/AA """
        return self._get_mean_and_samples_attribute('Vega_zero_flux')

    @property
    def Vega_zero_Jy(self):
        """ Vega flux zero point in Jansky (Jy) """
        return self._get_mean_and_samples_attribute('Vega_zero_Jy')

    @property
    def ST_zero_mag(self):
        """ ST magnitude zero point
        STmag = -2.5 * log10(f_lamb) -21.1
        """
        return 21.1

    @property
    def ST_zero_flux(self):
        """ ST flux zero point in erg/s/cm2/AA """
        return 10 ** (-0.4 * self.ST_zero_mag) * unit['erg/s/cm ** 2/AA']

    @property
    def ST_zero_Jy(self):
        """ ST flux zero point in Jansky (Jy) """
        return self._get_mean_and_samples_attribute('ST_zero_Jy')

    def to_Table(self, **kwargs):
        """ Export filter to a SimpleTable object

        Parameters
        ----------
        fname: str
            filename

        Uses `SimpleTable` parameters
        """
        mean_transmit, transmit_ = self.transmit
        data_ = {'WAVELENGTH': self._wavelength,
                 'THROUGHPUT': mean_transmit}
        for num, filterk in enumerate(transmit_, 1):
            data_['THROUGHPUT_{0:d}'.format(num)] = filterk
        data = SimpleTable(data_)

        if self.wavelength_unit is not None:
            data.header['WAVELENGTH_UNIT'] = self.wavelength_unit
        data.header['DETECTOR'] = self.dtype
        data.header['COMPNAME'] = self.name
        data.header['NAME'] = self.name
        data.set_comment('THROUGHPUT', 'filter throughput definition')
        data.set_comment('WAVELENGTH', 'filter wavelength definition')
        for num in range(1, len(transmit_) + 1):
            data.set_comment('THROUGHPUT_{0:d}'.format(num), 'filter throughput sample')
        data.set_comment('WAVELENGTH', self.wavelength_unit or 'AA')
        return data

    @classmethod
    def from_ascii(cls, fname, dtype='csv', **kwargs):
        """ Load filter from ascii file """
        lamb = kwargs.pop('lamb', None)
        name = kwargs.pop('name', None)
        detector = kwargs.pop('detector', 'photon')
        unit_ = kwargs.pop('unit', None)

        if not isinstance(fname, SimpleTable):
            t = SimpleTable(fname, dtype=dtype, **kwargs)
        else:
            t = fname
        w = t['WAVELENGTH'].astype(float)
        r = t['THROUGHPUT'].astype(float)
        keys = [k for k in t.keys() if 'THROUGHPUT_' in k]

        # update properties from file header
        detector = t.header.get('DETECTOR', detector)
        unit_    = t.header.get('WAVELENGTH_UNIT', unit_)

        # try from the comments in the header first
        if name in (None, 'None', 'none', ''):
            name = [k.split()[1]
                    for k in t.header.get('COMMENT', '').split('\n')
                    if 'COMPNAME' in k]
            name = ''.join(name).replace('"', '').replace("'", '')
        # if that did not work try the table header directly
        if name in (None, 'None', 'none', ''):
            name = t.header['NAME']

        if len(keys) > 0:
            samp = np.array([t[key] for key in keys])
            _filter = cls(w, r, samp, name=name, dtype=detector, unit=unit_)
        else:
            _filter = Filter(w, r, name=name, dtype=detector, unit=unit_)

        # reinterpolate if requested
        if lamb is not None:
            _filter = _filter.reinterp(lamb)

        return _filter


class Library(object):
    """ Common grounds for filter libraries """

    def __init__(self, source=__default__, *args, **kwargs):
        """ Construct the library """
        self.source = None

    def __repr__(self):
        return "Filter Library: {0}\n{1:s}".format(self.source, object.__repr__(self))

    def __enter__(self):
        """ Enter context """
        return self

    def __exit__(self,  *exc_info):
        """ end context """
        return False

    def __len__(self):
        """ Size of the library """
        return len(self.content)

    def to_csv(self, directory='./', progress=True, **kwargs):
        """ Export each filter into a csv file with its own name

        Parameters
        ----------
        directory: str
            directory to write into
        progress: bool
            show progress if set
        
        """
        from .helpers import progress_enumerate
        try:
            os.stat(directory)
        except Exception:
            os.mkdir(directory)
        with self as s:
            for _, k in progress_enumerate(s.content, desc='export', show_progress=progress):
                f = s[k]
                if f.wavelength_unit is None:
                    f.wavelength_unit = 'AA'
                f.write_to("{0:s}/{1:s}.csv".format(directory, f.name).lower(),
                           fmt="%.6f", **kwargs)

    def to_hdf(self, fname='filters.hd5', progress=True, **kwargs):
        """ Export each filter into a csv file with its own name

        Parameters
        ----------
        directory: str
            directory to write into
        progress: bool
            show progress if set

        """
        from .helpers import progress_enumerate
        with self as s:
            for _, k in progress_enumerate(s.content, desc='export', show_progress=progress):
                f = s[k]
                if f.wavelength_unit is None:
                    f.wavelength_unit = 'AA'
                f.write_to("{0:s}".format(fname),
                           tablename='/filters/{0}'.format(f.name),
                           createparents=True, append=True, silent=True, **kwargs)

    @classmethod
    def from_hd5(cls, filename, **kwargs):
        return HDF_Library(filename, **kwargs)

    @classmethod
    def from_ascii(cls, filename, **kwargs):
        return Ascii_Library(filename, **kwargs)

    @property
    def content(self):
        """ Get the content list """
        return self.get_library_content()

    def __getitem__(self, name):
        """ Make this object like a dictionary and load one or multiple filters """
        with self as s:
            try:
                f = s._load_filter(name)
            except TypeError:
                f = [s._load_filter(k) for k in name]
        return f

    def _load_filter(self, *args, **kwargs):
        """ Load a given filter from the library """
        raise NotImplementedError

    def get_library_content(self):
        """ get the content of the library """
        raise NotImplementedError

    def load_all_filters(self, interp=True, lamb=None):
        """ load all filters from the library """
        raise NotImplementedError

    def add_filter(self, f):
        """ add a filter to the library """
        raise NotImplementedError

    def find(self, name, case_sensitive=True):
        r = []
        if case_sensitive:
            _n = name.lower()
            for k in self.get_library_content():
                if _n in k.lower():
                    r.append(k)
        else:
            for k in self.content:
                if name in k:
                    r.append(k)
        return r


class Ascii_Library(Library):
    """ Interface one or multiple directory or many files as a filter library

    >>> lib = Ascii_Library(['ground', 'hst', 'myfilter.csv'])
    """
    def __init__(self, source):
        self.source = source

    def _load_filter(self, fname, interp=True, lamb=None, *args, **kwargs):
        """ Load a given filter from the library """
        try:
            fil = Filter.from_ascii(fname, *args, **kwargs)
        except Exception:
            content = self.content
            r = [k for k in content if fname in k]

            if len(r) <= 0:  # try all lower for filenames (ascii convention)
                r = [k for k in content if fname.lower() in k]

            if len(r) > 1:
                print("auto correction found multiple choices")
                print(r)
                raise ValueError('Refine name to one of {0}'.format(r))
            elif len(r) <= 0:
                raise ValueError('Cannot find filter {0}'.format(fname))
            else:
                fil = Filter.from_ascii(r[0], *args, **kwargs)
        if (interp is True) and (lamb is not None):
            return fil.reinterp(lamb)
        else:
            return fil

    def get_library_content(self):
        """ get the content of the library """
        from glob import glob
        try:
            os.path.isdir(self.source)
            lst = glob(self.source + '/*')
        except TypeError:
            lst = self.source
        dircheck = True
        while dircheck is True:
            dircheck = False
            newlst = []
            for entry in lst:
                if os.path.isdir(entry):
                    newlst.extend(glob(entry + '/*'))
                    dircheck = True
                else:
                    newlst.append(entry)
            lst = newlst
        return lst

    def load_all_filters(self, interp=True, lamb=None):
        """ load all filters from the library """
        return [self._load_filter(k, interp=interp, lamb=lamb) for k in self.content]

    def load_filters(self, names, interp=True, lamb=None, filterLib=None):
        """ load a limited set of filters

            Parameters
            ----------
            names: list[str]
                normalized names according to filtersLib

            interp: bool
                reinterpolate the filters over given lambda points

            lamb: ndarray[float, ndim=1]
                desired wavelength definition of the filter

            filterLib: path
                path to the filter library hd5 file

            Returns
            -------
            filters: list[filter]
                list of filter objects
        """
        filters = [self._load_filter(fname, interp=interp, lamb=lamb) for fname in names]
        return(filters)

    def add_filters(self, filter_object, fmt="%.6f", **kwargs):
        """ Add a filter to the library permanently

        Parameters
        ----------
        filter_object: Filter object
            filter to add
        """
        if not isinstance(filter_object, Filter):
            raise TypeError("Argument of type Filter expected. Got type {0}".format(type(filter_object)))

        if filter_object.wavelength_unit is None:
            raise AttributeError("Filter wavelength must have units for storage.")
        filter_object.write_to("{0:s}/{1:s}.csv".format(self.source,
                                                        filter_object.name).lower(),
                                fmt=fmt, **kwargs)


class HDF_Library(Library):
    """ Storage based on HDF """
    def __init__(self, source=__default__, mode='r'):
        self.source = source
        self.hdf = None
        self.mode = mode

    def __enter__(self):
        """ Enter context """
        if self.hdf is None:
            self.hdf = tables.open_file(self.source, self.mode)

        return self

    def __exit__(self, *exc_info):
        """ end context """
        if self.hdf is not None:
            self.hdf.close()
            self.hdf = None
        return False

    def _load_filter(self, fname, interp=True, lamb=None):
        """ Load a given filter from the library

        Parameters
        ----------
        fname: str
            normalized names according to filtersLib

        interp: bool, optional
            reinterpolate the filters over given lambda points

        lamb: ndarray[float, ndim=1]
            desired wavelength definition of the filter

        integrationFilter: bool, optional
            set True for specail integraion filter such as Qion or E_uv
            if set, lamb should be given

        Returns
        -------
        filter: Filter instance
            filter object
        """
        ftab = self.hdf
        if hasattr(fname, 'decode'):
            fnode    = ftab.get_node('/filters/' + fname.decode('utf8'))
        else:
            fnode    = ftab.get_node('/filters/' + fname)
        flamb    = fnode[:]['WAVELENGTH']
        transmit = fnode[:]['THROUGHPUT']
        dtype = 'photon'
        unit = None

        attrs = fnode.attrs
        if 'DETECTOR' in attrs:
            dtype = attrs['DETECTOR']
        if 'WAVELENGTH_UNIT' in attrs:
            unit = attrs['WAVELENGTH_UNIT']

        fil = Filter(flamb, transmit, name=fnode.name, dtype=dtype, unit=unit)

        if interp & (lamb is not None):
            fil = fil.reinterp(lamb)
        return fil

    def get_library_content(self):
        """ get the content of the library """
        with self as s:
            try:
                filters = s.hdf.root.content.cols.TABLENAME[:]
            except Exception:
                filters = list(s.hdf.root.filters._v_children.keys())
        if hasattr(filters[0], 'decode'):
            filters = [k.decode('utf8') for k in filters]
        return(filters)

    def load_all_filters(self, interp=True, lamb=None):
        """ load all filters from the library

        Parameters
        ----------
        interp: bool
            reinterpolate the filters over given lambda points

        lamb: ndarray[float, ndim=1]
            desired wavelength definition of the filter

        Returns
        -------
        filters: list[filter]
            list of filter objects
        """
        with self as s:
            filters = [s._load_filter(fname, interp=interp, lamb=lamb)
                       for fname in s.content ]
        return(filters)

    def load_filters(self, names, interp=True, lamb=None, filterLib=None):
        """ load a limited set of filters

            Parameters
            ----------
            names: list[str]
                normalized names according to filtersLib

            interp: bool
                reinterpolate the filters over given lambda points

            lamb: ndarray[float, ndim=1]
                desired wavelength definition of the filter

            filterLib: path
                path to the filter library hd5 file

            Returns
            -------
            filters: list[filter]
                list of filter objects
        """
        with self as s:
            filters = [s._load_filter(fname, interp=interp, lamb=lamb)
                       for fname in names]
        return(filters)

    def add_filter(self, f, **kwargs):
        """ Add a filter to the library permanently

        Parameters
        ----------
        f: Filter object
            filter to add
        """
        if not isinstance(f, Filter):
            raise TypeError("Argument of type Filter expected. Got type {0}".format(type(f)))

        if f.wavelength_unit is None:
            raise AttributeError("Filter wavelength must have units for storage.")

        f.write_to("{0:s}".format(self.source),
                   tablename='/filters/{0}'.format(f.name),
                   createparents=True,
                   **kwargs)


def get_library(fname=__default__, **kwargs):
    """ Finds the appropriate class to load the library """
    if os.path.isfile(fname):
        return HDF_Library(fname, **kwargs)
    else:
        return Ascii_Library(fname, **kwargs)
