import pandas as pd

def getRiesgo(data):
    #const riskScore = (
    #        ageWeight * 5 +
    #        smokingWeight * 3 +
    #        symptomsAvg * 4 +
    #        chronicWeight * 8 +
    #        geneticWeight * 6 +
    #        hemoptysisWeight * 10
    #);

    model_data = []
    model_data.append(data["air_pollution"])
    model_data.append(data["alcohol_use"])
    model_data.append(data["occupation_hazard"])
    model_data.append(data["genetic_risk"])
    model_data.append(data["chronic_lung_disease"])
    model_data.append(data["obesity"])
    model_data.append(data["smoking_level"])
    model_data.append(data["passive_smoker"])
    model_data.append(data["chest_pain"])
    model_data.append(data["hemoptysis_level"])
    model_data.append(data["fatigue"])
    model_data.append(data["weight_loss"])
    if data["weight_loss"]==None:
        model_data.append(0)
    model_data.append(data["shortness_of_breath"])
    model_data.append(data["wheezing"])
    model_data.append(data["swallowing_difficulty"])
    model_data.append(data["clubbing_nails"])

    total = 0
    count = 0
    for item in model_data:
        # convert to numeric; empty strings become NaN
        num = pd.to_numeric(item, errors="coerce")
        if pd.notna(num):
            total += num
        count += 1

    mean = total / count if count > 0 else 0

    avgW = pd.to_numeric(data["obesity"], errors="coerce")
    smoking = pd.to_numeric(data["smoking_level"], errors="coerce")
    chronicWeight = pd.to_numeric(data["chronic_lung_disease"], errors="coerce")
    geneticWeight = pd.to_numeric(data["genetic_risk"], errors="coerce")
    Hemo = pd.to_numeric(data["hemoptysis_level"], errors="coerce")

    riskScore = (mean * 4 +
                 avgW * 4 +
                 smoking * 3 +
                 chronicWeight * 8 +
                 geneticWeight * 6 +
                 Hemo * 10)
    return riskScore
