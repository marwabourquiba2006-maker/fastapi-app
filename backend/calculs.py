
def simulation(debit, ajout, concentration, temperature):

    # CONSTANTES DU PROCEDE
    residus = 20
    y0 = 0.10
    yR = 0.40
    Cp = 3.8
    lambda_v = 2300

    # VALIDATION DES DONNEES
    if debit <= residus:
        raise ValueError("Le débit doit être supérieur à 20 kg/h.")

    if ajout < 0:
        raise ValueError("L'ajout doit être positif.")

    if not 0 < concentration <= 100:
        raise ValueError("La concentration doit être entre 0 et 100 %.")

    if temperature < 20:
        raise ValueError("La température doit être supérieure ou égale à 20 °C.")

    # 1. FILTRATION
    m1 = debit - residus
    y1 = (debit * y0) / m1

    # 2. MELANGE
    m2 = m1 + ajout
    y2 = (m1 * y1 + ajout * yR) / m2

    # VERIFICATION DE LA CONCENTRATION
    x4 = concentration / 100

    if x4 < y2:
        pass
    else:
        raise ValueError(
            "La concentration finale doit être inférieure à la concentration après mélange."
        )

    # 3. CHAUFFAGE
    Q3 = m2 * Cp * (temperature - 20) / 3600

    # 4. EVAPORATION
    m4 = (m2 * y2) / x4
    mv = m2 - m4
    Q4 = mv * lambda_v / 3600

    # 5. REFROIDISSEMENT
    Q5 = m4 * Cp * (temperature - 25) / 3600

    # BILAN GLOBAL
    entrees = debit + ajout
    sorties = residus + mv + m4
    ecart = entrees - sorties

    return {
        "debit_filtration": round(m1, 2),
        "debit_melange": round(m2, 2),
        "concentration_melange": round(y2 * 100, 2),
        "puissance_chauffage": round(Q3, 2),
        "debit_vapeur": round(mv, 2),
        "debit_final": round(m4, 2),
        "puissance_evaporation": round(Q4, 2),
        "puissance_refroidissement": round(Q5, 2),
        "ecart_bilan": round(ecart, 6)
    }
