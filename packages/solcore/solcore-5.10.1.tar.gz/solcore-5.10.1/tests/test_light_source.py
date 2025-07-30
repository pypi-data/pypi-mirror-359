from pytest import approx


def test_register_conversion_function():
    from solcore.light_source.light_source import (
        REGISTERED_CONVERTERS,
        power_density_per_nm,
    )

    name = power_density_per_nm.__name__
    assert name in REGISTERED_CONVERTERS
    assert REGISTERED_CONVERTERS[name] == power_density_per_nm


def test_power_density_per_nm(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import power_density_per_nm

    expected, sp_fun = gauss_spectrum
    actual = power_density_per_nm(sp_fun, wavelength)
    assert actual == approx(expected)


def test_photon_flux_per_nm(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import photon_flux_per_nm
    from solcore.constants import c, h

    sp, sp_fun = gauss_spectrum
    expected = sp / (c * h * 1e9 / wavelength)

    actual = photon_flux_per_nm(sp_fun, wavelength)
    assert actual == approx(expected)


def test_power_density_per_m(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import power_density_per_m
    import numpy as np

    sp, sp_fun = gauss_spectrum
    expected = np.trapezoid(sp, wavelength)

    wl_m = wavelength * 1.0e-9
    actual = power_density_per_m(sp_fun, wl_m)
    actual = np.trapezoid(actual, wl_m)
    assert actual == approx(expected)


def test_photon_flux_per_m(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import photon_flux_per_m
    from solcore.constants import c, h

    sp, sp_fun = gauss_spectrum

    wl_m = wavelength * 1e-9
    expected = sp / (c * h / wavelength)
    actual = photon_flux_per_m(sp_fun, wl_m)
    assert actual == approx(expected)


def test_power_density_per_ev(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import power_density_per_ev
    from solcore import spectral_conversion_nm_ev

    sp, sp_fun = gauss_spectrum
    ev, expected = spectral_conversion_nm_ev(wavelength, sp)

    actual = power_density_per_ev(sp_fun, ev)
    assert actual == approx(expected)


def test_photon_flux_per_ev(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import photon_flux_per_ev
    from solcore import spectral_conversion_nm_ev
    from solcore.constants import q

    sp, sp_fun = gauss_spectrum
    ev, expected = spectral_conversion_nm_ev(wavelength, sp)

    actual = photon_flux_per_ev(sp_fun, ev)
    assert actual * q * ev == approx(expected)


def test_power_density_per_joule(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import power_density_per_joule
    from solcore import spectral_conversion_nm_ev
    from solcore.constants import q

    sp, sp_fun = gauss_spectrum
    ev, expected = spectral_conversion_nm_ev(wavelength, sp)

    actual = power_density_per_joule(sp_fun, ev * q)
    assert actual * q == approx(expected)


def test_photon_flux_per_joule(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import photon_flux_per_joule
    from solcore import spectral_conversion_nm_ev
    from solcore.constants import q

    sp, sp_fun = gauss_spectrum
    ev, expected = spectral_conversion_nm_ev(wavelength, sp)

    actual = photon_flux_per_joule(sp_fun, ev * q)
    assert actual * q ** 2 * ev == approx(expected)


def test_power_density_per_hz(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import power_density_per_hz
    from solcore import spectral_conversion_nm_hz

    sp, sp_fun = gauss_spectrum
    hz, expected = spectral_conversion_nm_hz(wavelength, sp)

    actual = power_density_per_hz(sp_fun, hz)
    assert actual == approx(expected)


def test_photon_flux_per_hz(wavelength, gauss_spectrum):
    from solcore.light_source.light_source import photon_flux_per_hz
    from solcore import spectral_conversion_nm_hz
    from solcore.constants import h

    sp, sp_fun = gauss_spectrum
    hz, expected = spectral_conversion_nm_hz(wavelength, sp)

    actual = photon_flux_per_hz(sp_fun, hz)
    assert actual * h * hz == approx(expected)


def test_wavelength_array_consistency():
    # GH 147
    from solcore.light_source import LightSource
    import numpy as np

    wl_arr = np.linspace(300, 1200, 10)*1e-9
    wl_arr2 = np.linspace(300, 1200, 20)*1e-9

    ls = LightSource(source_type='standard', version='AM1.5g', x=wl_arr,
                             output_units='photon_flux_per_m')
    assert ls.spectrum()[1].shape == wl_arr.shape
    assert ls.spectrum(x=wl_arr2)[1].shape == wl_arr2.shape


def test_spectral2():

    from solcore.light_source import LightSource
    import numpy as np

    wls = np.linspace(300, 4000, 10)*1e-9

    c_coefficient = [0.6, 14, 10]
    d_coefficient = [2, 10, 1, 6]

    aod_models = ['rural', 'urban', 'tropospheric', 'maritime',
                  [c_coefficient, d_coefficient]]

    for aod_mod in aod_models:
        ls = LightSource(source_type='SPECTRAL2', x=wls, output_units='photon_flux_per_m',
                           precipwater=1.0, turbidity=0.05,
                           aod_model=aod_mod,
                           latitude=-33.87 * np.pi / 180, longitude=-151.21 * np.pi / 180,
                           )
        assert ls.spectrum(np.array([500e-9]))[1] < 3.1e27
        assert ls.spectrum(np.array([500e-9]))[1] > 2.0e27

    # check if throws error with a different string:
    try:
        LightSource(
            source_type='SPECTRAL2', x=wls, output_units='photon_flux_per_m',
                           precipwater=1.0, turbidity=0.05,
                           aod_model='other',
                           latitude=-33.87 * np.pi / 180, longitude=-151.21 * np.pi / 180,
                           )
    except AssertionError:
        pass
    else:
        assert False
