import math
from typing import List, Union, Tuple

import torch
import random

from artist.util.utils import convert_3d_direction_to_4d_format

def calculateSunAngles(
        hour: int,
        minute: int,
        sec: int,
        day: int,
        month: int,
        year: int,
        observerLatitude: float,
        observerLongitude: float,
) -> Tuple[float, float]:
    # in- and outputs are in degree
    if (
            hour < 0 or hour > 23
            or minute < 0 or minute > 59
            or sec < 0 or sec > 59
            or day < 1 or day > 31
            or month < 1 or month > 12
    ):
        raise ValueError(
            "at least one value exceeded time range in calculateSunAngles")

    else:
        observerLatitudeInt = observerLatitude / 180.0 * math.pi
        observerLongitudeInt = observerLongitude / 180.0 * math.pi

        pressureInput = 1.01325  # Pressure in bar
        temperature = 20  # Temperature in °C

        UT = hour + minute / 60.0 + sec / 3600.0
        pressure = pressureInput / 1.01325
        delta_t = 0.0

        if month <= 2:
            dyear = year - 1.0
            dmonth = month + 12.0
        else:
            dyear = year
            dmonth = month

        trunc1 = math.floor(365.25 * (dyear - 2000))
        trunc2 = math.floor(30.6001 * (dmonth + 1))
        JD_t = trunc1 + trunc2 + day + UT / 24.0 - 1158.5
        t = JD_t + delta_t / 86400.0

        # standard JD and JDE
        # (useless for the computation, they are computed for completeness)
        # JDE = t + 2452640
        # JD = JD_t + 2452640

        # HELIOCENTRIC LONGITUDE
        # linear increase + annual harmonic
        ang = 0.0172019 * t - 0.0563
        heliocLongitude = (
                1.740940
                + 0.017202768683 * t
                + 0.0334118 * math.sin(ang)
                + 0.0003488 * math.sin(2.0 * ang)
        )

        # Moon perturbation
        heliocLongitude = \
            heliocLongitude + 0.0000313 * math.sin(0.2127730 * t - 0.585)
        # Harmonic correction
        heliocLongitude = (
                heliocLongitude
                + 0.0000126 * math.sin(0.004243 * t + 1.46)
                + 0.0000235 * math.sin(0.010727 * t + 0.72)
                + 0.0000276 * math.sin(0.015799 * t + 2.35)
                + 0.0000275 * math.sin(0.021551 * t - 1.98)
                + 0.0000126 * math.sin(0.031490 * t - 0.80)
        )

        # END HELIOCENTRIC LONGITUDE CALCULATION
        # Correction to longitude due to notation
        t2 = t / 1000.0
        heliocLongitude = (
                heliocLongitude
                + (
                        (
                                (-0.000000230796 * t2 + 0.0000037976) * t2
                                - 0.000020458
                        ) * t2
                        + 0.00003976
                ) * t2 * t2
        )

        delta_psi = 0.0000833 * math.sin(0.0009252 * t - 1.173)

        # Earth axis inclination
        epsilon = (
                -0.00000000621 * t
                + 0.409086
                + 0.0000446 * math.sin(0.0009252 * t + 0.397)
        )
        # Geocentric global solar coordinates
        geocSolarLongitude = heliocLongitude + math.pi + delta_psi - 0.00009932

        s_lambda = math.sin(geocSolarLongitude)
        rightAscension = math.atan2(
            s_lambda * math.cos(epsilon),
            math.cos(geocSolarLongitude),
        )

        declination = math.asin(math.sin(epsilon) * s_lambda)

        # local hour angle of the sun
        hourAngle = (
                6.30038809903 * JD_t
                + 4.8824623
                + delta_psi * 0.9174
                + observerLongitudeInt
                - rightAscension
        )

        c_lat = math.cos(observerLatitudeInt)
        s_lat = math.sin(observerLatitudeInt)
        c_H = math.cos(hourAngle)
        s_H = math.sin(hourAngle)

        # Parallax correction to Right Ascension
        d_alpha = -0.0000426 * c_lat * s_H
        # topOCRightAscension = rightAscension + d_alpha
        # topOCHourAngle = hourAngle - d_alpha

        # Parallax correction to Declination
        topOCDeclination = \
            declination - 0.0000426 * (s_lat - declination * c_lat)

        s_delta_corr = math.sin(topOCDeclination)
        c_delta_corr = math.cos(topOCDeclination)
        c_H_corr = c_H + d_alpha * s_H
        s_H_corr = s_H - d_alpha * c_H

        # Solar elevation angle, without refraction correction
        elevation_no_refrac = math.asin(
            s_lat * s_delta_corr
            + c_lat * c_delta_corr * c_H_corr
        )

        # Refraction correction:
        # it is calculated only if elevation_no_refrac > elev_min
        elev_min = -0.01

        if elevation_no_refrac > elev_min:
            refractionCorrection = (
                    0.084217 * pressure
                    / (273.0 + temperature)
                    / math.tan(
                elevation_no_refrac
                + 0.0031376 / (elevation_no_refrac + 0.089186)
            )
            )
        else:
            refractionCorrection = 0

        # elevationAngle = \
        #     np.pi / 2 - elevation_no_refrac - refractionCorrection
        elevationAngle = elevation_no_refrac + refractionCorrection
        elevationAngle = elevationAngle * 180 / math.pi

        # Ensure elevation angle is greater than 30, otherwise recalculate
        #while elevationAngle <= 30:
            # Print warning or log if desired
            #print(f"Elevation angle too low: {elevationAngle:.2f}°")

            # Generate new random time values
            #hour = random.randint(0, 23)
            #minute = random.randint(0, 59)
            #sec = random.randint(0, 59)
            #day = random.randint(1, 31)
            #month = random.randint(1, 12)
            #year = random.randint(2020, 2024)

            # Recalculate the sun angles with the new random time
            #print(year, month, day, hour, minute, sec)
            #azimuthAngle, elevationAngle = calculateSunAngles(
            #    hour, minute, sec, day, month, year, observerLatitude, observerLongitude
            #)

        # azimuthAngle = math.atan2(
        #     s_H_corr,
        #     c_H_corr * s_lat - s_delta_corr/c_delta_corr * c_lat,
        # )
        azimuthAngle = -math.atan2(
            s_H_corr,
            c_H_corr * s_lat - s_delta_corr / c_delta_corr * c_lat,
        )
        azimuthAngle = azimuthAngle * 180 / math.pi


    return azimuthAngle, elevationAngle


def ae_to_vec(azi: torch.Tensor, ele: torch.Tensor) -> torch.Tensor:
    """
    Convert azimuth and elevation angles to 3D unit vectors.

    Parameters
    ----------
    azi : torch.Tensor
        Azimuth angles in degrees.
    ele : torch.Tensor
        Elevation angles in degrees.

    Returns
    -------
    torch.Tensor
        A tensor of shape (n, 3) representing 3D unit vectors.
    """
    # Convert degrees to radians for trigonometric calculations
    azi_rad = torch.deg2rad(azi)
    ele_rad = torch.deg2rad(ele)

    # Compute Cartesian coordinates
    x = torch.cos(ele_rad) * torch.cos(azi_rad)
    y = torch.cos(ele_rad) * torch.sin(azi_rad)
    z = torch.sin(ele_rad)

    # Combine into a single tensor
    return torch.stack([x, y, z], dim=1)  # Shape: (n, 3)


def get_sun_array(
        *datetime: List[int],
        **observer: float,
) -> Tuple[torch.Tensor, List[List[Union[int, float]]]]:
    """Arguments must be in descending order (years, months, days, ...)."""
    years = [2021]
    months = [6]
    days = [21]
    hours = list(range(6, 19))
    minutes = [0, 30]
    secs = [0]

    num_args = len(datetime)
    if num_args == 0:
        print("generate values for 21.06.2021")
    if num_args >= 1:
        years = datetime[0]
        if num_args >= 2:
            months = datetime[1]
            if num_args >= 3:
                days = datetime[2]
                if num_args >= 4:
                    hours = datetime[3]
                    if num_args >= 5:
                        minutes = datetime[4]
                        if num_args >= 6:
                            secs = datetime[5]

    observerLatitude = observer.get('latitude', 50.92)
    observerLongitude = observer.get('longitude', 6.36)

    # sunAngles = np.empty((3,1440,2))
    extras = []
    ae = []
    for year in years:
        for month in months:
            for day in days:
                for hour in hours:
                    for minute in minutes:
                        for sec in secs:
                            azi, ele = calculateSunAngles(
                                hour,
                                minute,
                                sec,
                                day,
                                month,
                                year,
                                observerLatitude,
                                observerLongitude,
                            )
                            extras.append([
                                year,
                                month,
                                day,
                                hour,
                                minute,
                                sec,
                                azi,
                                ele,
                            ])
                            ae.append([azi, ele])
    ae = torch.tensor(ae)
    sun_vecs = ae_to_vec(ae[:, 0], ae[:, 1])
    return sun_vecs, extras

def random_sun_positions(num_positions, device):

    sun_vecs_list = []
    extras_list = []

    for i in range(num_positions):
        year = [2024]
        month = [6]
        day = [21]
        hour = [random.randint(6, 19)]
        minute = [random.randint(0, 59)]
        sec = [random.randint(0, 59)]

        #print(year, month, day, hour, minute, sec)
        sun_vecs, extras = get_sun_array(year, month, day, hour, minute, sec)
        #print(sun_vecs, extras)

        while extras[-1][-1] < 30:
            year = [2024]
            month = [6]
            day = [21]
            hour = [random.randint(6, 19)]
            minute = [random.randint(0, 59)]
            sec = [random.randint(0, 59)]
            sun_vecs, extras = get_sun_array(year, month, day, hour, minute, sec)

        #print("final sun vecs")
        #print(sun_vecs, extras)
        #print(sun_vecs[0, 0])
        #print("sum")
        #print(math.sqrt((sun_vecs[0, 0] ** 2) + (sun_vecs[0, 1] ** 2) + (sun_vecs[0, 2] ** 2)))

        sun_vecs = convert_3d_direction_to_4d_format(sun_vecs, device=device)
        sun_vecs = sun_vecs.squeeze(0)
        sun_vecs_list.append(sun_vecs)
        extras_list.append(extras)

    return sun_vecs_list, extras_list