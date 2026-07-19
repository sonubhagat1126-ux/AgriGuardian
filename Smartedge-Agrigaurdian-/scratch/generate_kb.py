"""
SmartEdge AgriGuardian — Knowledge Base Expansion Generator
=============================================================
Generates the complete, production-grade knowledge_base.json file
covering all 15 PlantVillage categories with full agricultural schemas,
safe treatment recommendations, and structured action_plan objects.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
KB_PATH_1 = os.path.join(PROJECT_ROOT, "knowledge-base", "knowledge_base.json")
KB_PATH_2 = os.path.join(PROJECT_ROOT, "arduino_backend", "modules", "knowledge_base", "knowledge_base.json")

diseases_data = [
    {
        "id": "Pepper__bell___Bacterial_spot",
        "name": "Pepper Bell Bacterial Spot",
        "crop": "Pepper (Bell)",
        "disease": "Pepper Bell Bacterial Spot",
        "scientific_name": "Xanthomonas euvesicatoria / Xanthomonas vesicatoria",
        "disease_type": "Bacterial",
        "severity": "High",
        "overview": "Bacterial spot affects leaves, stems, and fruits of pepper plants. It causes small, water-soaked dark spots that enlarge into brown necrotic lesions, leading to severe defoliation and yield loss in warm, wet weather.",
        "symptoms": [
            "Small water-soaked dark spots on leaves",
            "Brown lesions with yellow halos on leaf margins",
            "Premature leaf drop causing sunscald on fruits",
            "Raised scab-like spots on pepper fruit"
        ],
        "causes": [
            "Bacterial pathogen Xanthomonas vesicatoria",
            "Infected seeds or crop debris",
            "Splashing water and high relative humidity"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": [
            "Temperature between 24°C and 30°C",
            "High relative humidity (>85%)",
            "Overhead sprinkler irrigation or frequent rain"
        ],
        "spread_method": "Spread by wind-driven rain, splashing water, contaminated tools, and infected seeds.",
        "early_stage": "Tiny water-soaked spots (1-3mm) appear on lower leaf surfaces.",
        "middle_stage": "Spots darken to dark brown with yellow chlorotic borders; leaves start turning yellow.",
        "severe_stage": "Widespread leaf necrosis, heavy defoliation, and fruit scarring.",
        "organic_treatment": [
            "Neem oil spray (5ml per liter water) every 7 days",
            "Copper hydroxide / Copper oxychloride organic formulation spray",
            "Garlic-chilli extract spray as natural antimicrobial"
        ],
        "biological_control": [
            "Apply Bacillus subtilis bio-fungicide to soil and foliage",
            "Use Pseudomonas fluorescens seed treatment"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP (2.5g/L) mixed with Streptocycline (0.1g/L)",
            "Kashugamycin / Bactericide application as per local state agricultural guidelines"
        ],
        "recommended_fungicides": ["Copper Oxychloride 50% WP", "Copper Hydroxide 77% WP"],
        "recommended_bactericides": ["Streptocycline", "Kasugamycin 3% SL"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK (19-19-19)", "Potash for immune strength"],
        "avoid_fertilizers": ["Excess Nitrogen (Urea) which softens plant tissue"],
        "micronutrients": ["Zinc Sulphate", "Boron spray for fruit development"],
        "watering_advice": "Irrigate at soil level using drip system. Never spray water directly over pepper foliage.",
        "soil_management": "Maintain well-drained soil with pH 6.0-6.8. Add organic compost and avoid waterlogging.",
        "weather_precautions": "Avoid field operations when leaves are wet. Apply protective copper sprays before monsoon rains.",
        "prevention": [
            "Use certified disease-free seeds",
            "Practice 2-3 year crop rotation with non-solanaceous crops",
            "Destroy infected crop residue after harvest"
        ],
        "do": [
            "Prune lower leaves that touch the soil",
            "Disinfect pruning tools with 70% alcohol",
            "Ensure wide plant spacing (45-60cm)"
        ],
        "dont": [
            "Do not overhead irrigate during hot afternoons",
            "Do not work in wet fields",
            "Do not apply excessive nitrogen fertilizers"
        ],
        "recovery_time": "10-14 Days after treatment initiation",
        "yield_loss": "Potential 20-50% loss if defoliation occurs during flowering",
        "harvest_safety": "Observe 7-10 day pre-harvest interval (PHI) after copper/chemical sprays",
        "nearby_crop_risk": "High risk to nearby tomato and eggplant crops",
        "next_monitoring": "Inspect plant foliage every 3 days",
        "emergency_action": "Isolate infected area, remove severely diseased leaves, and apply copper bactericide immediately.",
        "farmer_tips": [
            "khet mein paani ikatha mat hone do",
            "tamatar aur pyaz ke sath crop rotation karo",
            "beej ko pehle treatment dekar hi boen"
        ],
        "faqs": [
            {
                "question": "Kya neem oil bacterial spot ko poori tarah theek kar sakta hai?",
                "answer": "Neem oil shuruaati stage mein bacteria ke spread ko rokta hai. Severe infection mein Copper Oxychloride spray zaroori hota hai."
            },
            {
                "question": "Kya bimar patte nikalne chahiye?",
                "answer": "Haan, jin patton par daag hain unhe turant kaat kar khet se door jala dein."
            }
        ],
        "action_plan": {
            "immediate_action": [
                "Pluck and safely burn all severely spotted lower leaves",
                "Stop overhead watering immediately"
            ],
            "today": [
                "Remove infected leaves and dispose outside field",
                "Spray Copper Oxychloride (2.5g/L) mixed with Streptocycline (0.1g/L) in evening"
            ],
            "next_3_days": [
                "Keep leaves dry and inspect for new water-soaked spots",
                "Ensure drip line is working properly without leaks"
            ],
            "next_week": [
                "Repeat copper spray if humid weather persists",
                "Apply Potassium / Micronutrient foliar spray to boost vigor"
            ],
            "monitoring_schedule": ["Inspect leaf undersides every 3 days"],
            "emergency_conditions": ["If over 30% foliage turns brown or fruit scabbing appears"],
            "expected_recovery": "10-14 Days",
            "success_indicators": [
                "No new water-soaked spots on young leaves",
                "New growth is healthy and bright green"
            ],
            "warning_signs": [
                "Rapid yellowing of entire middle foliage",
                "Scab lesions spreading to green pepper pods"
            ]
        }
    },
    {
        "id": "Pepper__bell___healthy",
        "name": "Pepper Bell Healthy",
        "crop": "Pepper (Bell)",
        "disease": "Healthy Crop",
        "scientific_name": "Capsicum annuum",
        "disease_type": "None",
        "severity": "None",
        "overview": "The pepper plant is healthy, vigorous, and free from bacterial, fungal, or viral symptoms.",
        "symptoms": ["No disease symptoms present", "Foliage is vibrant green and firm"],
        "causes": ["Good agricultural practices", "Balanced nutrition and moisture"],
        "affected_parts": ["None"],
        "favorable_conditions": ["Temperature 20°C-28°C", "Moderate soil moisture", "Full sunlight"],
        "spread_method": "None",
        "early_stage": "Optimal vegetative growth.",
        "middle_stage": "Healthy flowering and pod setting.",
        "severe_stage": "None",
        "organic_treatment": ["Preventive Neem oil spray (3ml/L) once every 14 days"],
        "biological_control": ["Preventive application of Trichoderma viride to root zone"],
        "chemical_treatment": ["None required"],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK 19-19-19", "Organic Vermicompost"],
        "avoid_fertilizers": ["Excess Nitrogen"],
        "micronutrients": ["General micronutrient foliar spray once a month"],
        "watering_advice": "Maintain regular moisture level without waterlogging.",
        "soil_management": "Keep soil aerated and mulched.",
        "weather_precautions": "Protect from extreme heatwaves or waterlogging during storm events.",
        "prevention": ["Maintain current watering and weeding practices"],
        "do": ["Continue regular field monitoring", "Use organic mulch"],
        "dont": ["Do not overwater", "Do not over-fertilize"],
        "recovery_time": "Already healthy",
        "yield_loss": "0%",
        "harvest_safety": "Safe for regular harvest",
        "nearby_crop_risk": "Low",
        "next_monitoring": "Inspect after 7 days",
        "emergency_action": "None required.",
        "farmer_tips": [
            "khet mein safai rakhein",
            "drip se paani dein",
            "samay par vermicompost daalein"
        ],
        "faqs": [
            {
                "question": "Kya swasth paudhe par spray karna chahiye?",
                "answer": "Keval bimaari se bachav ke liye har 15 din mein ek baar Neem oil spray kar sakte hain."
            }
        ],
        "action_plan": {
            "immediate_action": ["Continue normal crop care routine"],
            "today": ["Maintain standard drip irrigation schedule", "Check for early pest signs"],
            "next_3_days": ["Monitor soil moisture"],
            "next_week": ["Apply balanced organic manure"],
            "monitoring_schedule": ["Inspect field weekly"],
            "emergency_conditions": ["None"],
            "expected_recovery": "Already Healthy",
            "success_indicators": ["Vigorous green growth", "Abundant flowers and pods"],
            "warning_signs": ["Any sudden leaf curling or yellow spots"]
        }
    },
    {
        "id": "Potato___Early_blight",
        "name": "Potato Early Blight",
        "crop": "Potato",
        "disease": "Potato Early Blight",
        "scientific_name": "Alternaria solani",
        "disease_type": "Fungal",
        "severity": "Medium",
        "overview": "Early blight is a major fungal disease affecting potato foliage and tubers. It causes characteristic target-board concentric dark brown spots on older leaves first.",
        "symptoms": [
            "Dark brown concentric rings (target spot pattern) on leaves",
            "Yellowing around brown spots",
            "Lower leaves turn brown and drop off",
            "Dry brown rot on tubers near surface"
        ],
        "causes": [
            "Fungal pathogen Alternaria solani",
            "Overwintering in soil or potato crop residue",
            "Warm temperatures and alternating wet/dry weather"
        ],
        "affected_parts": ["Foliage", "Stems", "Tubers"],
        "favorable_conditions": [
            "Temperature 24°C-29°C",
            "Frequent heavy dew or light rain",
            "Nutrient-stressed or aging crops"
        ],
        "spread_method": "Fungal spores spread easily by wind, rain splashes, insects, and farm machinery.",
        "early_stage": "Small dark brown spots (1-2mm) with yellow halos appear on lower mature leaves.",
        "middle_stage": "Spots enlarge up to 1cm exhibiting concentric rings (target pattern); leaves wilt.",
        "severe_stage": "Complete foliar blight, defoliation, and stem collapse.",
        "organic_treatment": [
            "Spray Copper Oxychloride or Bordeaux mixture (1%)",
            "Neem oil 5ml/L spray every 7 days",
            "Garlic-chilli homemade bio-extract spray"
        ],
        "biological_control": [
            "Foliar spray of Trichoderma harzianum (5g/L)",
            "Soil application of Pseudomonas fluorescens"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP (2g/L) or Chlorothalonil 75% WP (2g/L)",
            "Systemic fungicide Difenoconazole 25% EC (0.5ml/L) or Azoxystrobin 23% SC (1ml/L)"
        ],
        "recommended_fungicides": ["Mancozeb 75% WP", "Difenoconazole 25% EC", "Azoxystrobin 23% SC"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Potassium Chloride / MOP for plant resistance", "Balanced NPK"],
        "avoid_fertilizers": ["Excessive Nitrogen without Potassium"],
        "micronutrients": ["Magnesium Sulphate", "Zinc spray"],
        "watering_advice": "Water in early morning so foliage dries quickly. Avoid sprinkler irrigation.",
        "soil_management": "Ensure high organic matter content, crop rotation with legumes, and proper earthing up.",
        "weather_precautions": "Spray protective contact fungicides before humid cloudy spells.",
        "prevention": [
            "Plant certified disease-free seed tubers",
            "Maintain proper earthing up to protect tubers",
            "Practice 3-year crop rotation"
        ],
        "do": [
            "Remove affected lower leaves promptly",
            "Destroy crop debris post-harvest",
            "Balance NPK fertilization"
        ],
        "dont": [
            "Do not leave harvested tubers exposed to fungal spores",
            "Do not overhead irrigate late in the evening"
        ],
        "recovery_time": "10-12 Days",
        "yield_loss": "15-30% if untreated during tuber initiation stage",
        "harvest_safety": "7-14 Days Pre-Harvest Interval (PHI) after systemic fungicide application",
        "nearby_crop_risk": "Moderate risk to tomato and pepper crops",
        "next_monitoring": "Inspect foliage every 3-4 days",
        "emergency_action": "Spray Difenoconazole or Mancozeb immediately and remove severely blighted lower leaves.",
        "farmer_tips": [
            "nichli pattiya jinpar gol daag ho unhe hata dein",
            "shaam ke samay paani na dein",
            "mancozeb ka spray 10 din mein karein"
        ],
        "faqs": [
            {
                "question": "Early blight aur Late blight mein kya fark hai?",
                "answer": "Early blight mein patte par gol chakkar (target ring) jaise brown daag hote hain. Late blight mein patte sadne lagte hain aur safed fafundi aati hai."
            }
        ],
        "action_plan": {
            "immediate_action": [
                "Remove and burn old blighted lower leaves near soil level",
                "Ensure morning irrigation only"
            ],
            "today": [
                "Pluck infected leaves with target-ring spots",
                "Spray Mancozeb 75% WP (2g/L) thoroughly over foliage"
            ],
            "next_3_days": [
                "Check middle canopy for new concentric spots",
                "Keep soil mounded (earthing up) around stem base"
            ],
            "next_week": [
                "Apply systemic Difenoconazole spray if spots expand",
                "Apply Potassium sulfate to strengthen tuber growth"
            ],
            "monitoring_schedule": ["Inspect foliage every 3 days"],
            "emergency_conditions": ["If more than 20% of lower canopy collapses"],
            "expected_recovery": "10-12 Days",
            "success_indicators": [
                "No new target spots on upper canopy leaves",
                "Healthy new leaf emergence"
            ],
            "warning_signs": [
                "Target spots appearing on top young leaves",
                "Stems developing brown dry lesions"
            ]
        }
    },
    {
        "id": "Potato___Late_blight",
        "name": "Potato Late Blight",
        "crop": "Potato",
        "disease": "Potato Late Blight",
        "scientific_name": "Phytophthora infestans",
        "disease_type": "Oomycete / Fungal-like",
        "severity": "Critical",
        "overview": "Late blight is the most destructive disease of potatoes. It causes rapid rot of foliage and tubers. Under wet humid conditions, it can destroy an entire field in 3-5 days.",
        "symptoms": [
            "Water-soaked dark green to purplish-black lesions on leaves",
            "White cottony fungal growth on underside of leaves in moist weather",
            "Rapid rotting and foul odor from blighted foliage",
            "Reddish-brown dry rot inside potato tubers"
        ],
        "causes": [
            "Pathogen Phytophthora infestans",
            "Cool temperatures (15°C-22°C) combined with high humidity (>90%)",
            "Wind-blown sporangia from infected neighboring fields"
        ],
        "affected_parts": ["Leaves", "Stems", "Tubers"],
        "favorable_conditions": [
            "Temperature 12°C-22°C",
            "Continuous high humidity or fog/dew for >10 hours",
            "Frequent rainfall"
        ],
        "spread_method": "Airborne sporangia travel miles in fog/wind. Water-borne zoospores wash into soil to infect tubers.",
        "early_stage": "Pale green or dark water-soaked spots appear on leaf tips or edges.",
        "middle_stage": "Lesions expand rapidly turning purplish-black; white downy mold appears on underside.",
        "severe_stage": "Entire field canopy wilts, turns black, and dies with characteristic rotting smell.",
        "organic_treatment": [
            "Spray Bordeaux mixture (1%) or Copper Oxychloride (3g/L) preventively",
            "Bio-fungicide Trichoderma harzianum soil drenching"
        ],
        "biological_control": [
            "Pseudomonas fluorescens foliar spray",
            "Bacillus subtilis biological barrier application"
        ],
        "chemical_treatment": [
            "Systemic spray: Cymoxanil 8% + Mancozeb 64% WP (2g/L) or Metalaxyl 8% + Mancozeb 64% WP (2g/L)",
            "Curative spray: Dimethomorph 50% WP (1g/L) or Fenamidone + Mancozeb"
        ],
        "recommended_fungicides": ["Cymoxanil + Mancozeb", "Metalaxyl + Mancozeb (Ridomil Gold)", "Dimethomorph 50% WP"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Potassium Nitrate (13-0-45)", "Avoid nitrogen during blight outbreak"],
        "avoid_fertilizers": ["Urea / Excessive Nitrogen"],
        "micronutrients": ["Zinc", "Boron"],
        "watering_advice": "Stop all overhead irrigation immediately. Switch to low drip irrigation or halt watering.",
        "soil_management": "Ensure high ridge earthing up (15-20cm) to prevent zoospores from washing down to tubers.",
        "weather_precautions": "Must spray systemic fungicides BEFORE fog/rain events when late blight warnings are issued.",
        "prevention": [
            "Use certified blight-resistant seed tubers",
            "Perform proper high earthing up",
            "Destroy cull piles and self-sown potato plants"
        ],
        "do": [
            "Cut vines (haulm destruction) 10-14 days before harvest if blight attacks",
            "Spray systemic fungicides at first sign of disease in locality",
            "Harvest only in dry weather"
        ],
        "dont": [
            "Do not irrigate during cloudy humid weather",
            "Do not harvest when soil is wet",
            "Do not store blighted tubers with healthy ones"
        ],
        "recovery_time": "7-10 Days (requires immediate systemic action)",
        "yield_loss": "Up to 100% total crop loss if unmanaged during tuber development",
        "harvest_safety": "Observe 14-day Pre-Harvest Interval (PHI) after systemic fungicide treatment",
        "nearby_crop_risk": "Extreme risk to all nearby tomato and potato fields",
        "next_monitoring": "Inspect daily during fog/humid periods",
        "emergency_action": "Cut and destroy heavily blighted plants, stop watering, and immediately apply Metalaxyl + Mancozeb systemic spray.",
        "farmer_tips": [
            "kohar ya dhund ke mausam mein turant ridomil gold spray karein",
            "paudho ki mitti oonchi chadhayein taaki aaloo sadne se bachein",
            "khudai se 10 din pehle patte kaat dein"
        ],
        "faqs": [
            {
                "question": "Kya late blight wala aaloo khana safe hai?",
                "answer": "Sadhe hue aaloo nahi khane chahiye. Unka swad kharab hota hai aur infection hota hai."
            },
            {
                "question": "Baarish ke mausam mein kaise bachein?",
                "answer": "Baarish se pehle Copper Oxychloride ya Ridomil Gold ka protective spray zaroor karein."
            }
        ],
        "action_plan": {
            "immediate_action": [
                "Halt all irrigation immediately",
                "Apply systemic fungicide (Metalaxyl + Mancozeb) within 12 hours"
            ],
            "today": [
                "Stop watering the field",
                "Spray Metalaxyl + Mancozeb (2g/L) or Cymoxanil + Mancozeb",
                "High earthing-up around plant bases to seal tubers"
            ],
            "next_3_days": [
                "Monitor underside of leaves for white cottony mold daily",
                "Check neighboring plants for black water-soaked lesions"
            ],
            "next_week": [
                "Re-apply Dimethomorph (1g/L) if overcast humid weather continues",
                "Perform haulm cutting (destroy foliage) if infection reaches >50% to save tubers"
            ],
            "monitoring_schedule": ["Inspect field daily"],
            "emergency_conditions": [
                "White mold on undersides spreading rapidly across 10% of field",
                "Canopy turning black with foul rotting odor"
            ],
            "expected_recovery": "7-10 Days",
            "success_indicators": [
                "Black lesions dry up and stop expanding",
                "White mold growth disappears on undersides"
            ],
            "warning_signs": [
                "Rapid canopy collapse overnight",
                "Tubers turning brown and soft in upper soil"
            ]
        }
    },
    {
        "id": "Potato___healthy",
        "name": "Potato Healthy",
        "crop": "Potato",
        "disease": "Healthy Crop",
        "scientific_name": "Solanum tuberosum",
        "disease_type": "None",
        "severity": "None",
        "overview": "The potato crop is healthy, vigorous, and exhibiting clean foliage with robust tuber growth.",
        "symptoms": ["No disease symptoms present", "Deep green healthy canopy"],
        "causes": ["Good seed selection and soil management"],
        "affected_parts": ["None"],
        "favorable_conditions": ["Temperature 15°C-24°C", "Well-drained fertile loam", "Moderate moisture"],
        "spread_method": "None",
        "early_stage": "Healthy seedling emergence.",
        "middle_stage": "Active canopy growth and tuber initiation.",
        "severe_stage": "None",
        "organic_treatment": ["Preventive Trichoderma viride soil application"],
        "biological_control": ["Preventive Neem oil (3ml/L) spray every 14 days"],
        "chemical_treatment": ["None required"],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["NPK 10-26-26", "Organic Compost"],
        "avoid_fertilizers": ["Excess Nitrogen late in season"],
        "micronutrients": ["Zinc", "Magnesium"],
        "watering_advice": "Maintain soil moisture at 60-70% field capacity during tuber bulking.",
        "soil_management": "Perform proper earthing up at 30 days after planting.",
        "weather_precautions": "Keep protective copper spray handy for unexpected overcast wet weather.",
        "prevention": ["Maintain crop rotation and proper earthing up"],
        "do": ["Keep field weed-free", "Monitor undersides of leaves"],
        "dont": ["Do not over-irrigate close to harvest"],
        "recovery_time": "Already healthy",
        "yield_loss": "0%",
        "harvest_safety": "Safe for regular harvest",
        "nearby_crop_risk": "Low",
        "next_monitoring": "Inspect field every 7 days",
        "emergency_action": "None required.",
        "farmer_tips": [
            "aaloo ki mitti samay par chadhayein",
            "halki sinchai karein",
            "khet ko saaf rakhein"
        ],
        "faqs": [
            {
                "question": "Swasth aaloo ki kheti mein kitni sinchai chahiye?",
                "answer": "Tuber bulking stage par har 7-10 din mein halki sinchai zaroori hoti hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Maintain current care routine"],
            "today": ["Perform regular field inspection", "Verify drip/furrow irrigation flow"],
            "next_3_days": ["Monitor soil moisture level"],
            "next_week": ["Apply earthing up if plants are 30cm tall"],
            "monitoring_schedule": ["Inspect weekly"],
            "emergency_conditions": ["None"],
            "expected_recovery": "Already Healthy",
            "success_indicators": ["Vigorous green leafy canopy", "Healthy stem growth"],
            "warning_signs": ["Any sudden brown spots or leaf curling"]
        }
    },
    {
        "id": "Tomato_Bacterial_spot",
        "name": "Tomato Bacterial Spot",
        "crop": "Tomato",
        "disease": "Tomato Bacterial Spot",
        "scientific_name": "Xanthomonas perforans / Xanthomonas vesicatoria",
        "disease_type": "Bacterial",
        "severity": "High",
        "overview": "Bacterial spot is a widespread tomato disease causing small dark greasy spots on leaves and scabby lesions on green fruits, leading to leaf drop and severe sunscald.",
        "symptoms": [
            "Small dark brown, water-soaked leaf spots",
            "Yellowing around leaf lesions",
            "Premature defoliation",
            "Raised dark scab-like spots on green tomatoes"
        ],
        "causes": [
            "Pathogen Xanthomonas species",
            "Contaminated seeds or plant debris",
            "Warm rainy weather and overhead watering"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": ["Temperature 25°C-30°C", "High humidity", "Frequent splashing rain"],
        "spread_method": "Wind-blown rain, overhead irrigation, splashing water, and farm workers' hands/tools.",
        "early_stage": "Tiny brown water-soaked specks (1-3mm) on foliage.",
        "middle_stage": "Spots enlarge, turn dark brown with yellow borders; lower leaves drop off.",
        "severe_stage": "Major defoliation exposing green fruit to sunscald; fruit scabbing.",
        "organic_treatment": [
            "Spray Copper Hydroxide or Copper Oxychloride (2.5g/L)",
            "Neem oil 5ml/L foliar spray every 7 days"
        ],
        "biological_control": ["Bacillus subtilis bio-bactericide foliar application"],
        "chemical_treatment": ["Copper Oxychloride 50% WP (2.5g/L) + Streptocycline (0.1g/L) spray"],
        "recommended_fungicides": ["Copper Oxychloride 50% WP", "Copper Hydroxide 77% WP"],
        "recommended_bactericides": ["Streptocycline", "Kasugamycin 3% SL"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Calcium Nitrate", "Potassium Sulfate"],
        "avoid_fertilizers": ["Excessive Urea / Nitrogen"],
        "micronutrients": ["Boron", "Zinc"],
        "watering_advice": "Use drip irrigation. Avoid overhead sprinklers.",
        "soil_management": "Mulch soil surface with straw to prevent rain splash from soil.",
        "weather_precautions": "Apply protective copper sprays before rain spells.",
        "prevention": [
            "Use certified disease-free seeds",
            "Practice 2-year crop rotation",
            "Mulch beds to reduce soil splashing"
        ],
        "do": ["Prune lower branches up to 30cm from ground", "Stake plants for air movement"],
        "dont": ["Do not handle plants when foliage is wet", "Do not overhead irrigate"],
        "recovery_time": "10-14 Days",
        "yield_loss": "20-40% due to defoliation and fruit lesions",
        "harvest_safety": "Observe 7-day PHI after copper spray",
        "nearby_crop_risk": "High risk to peppers and eggplants",
        "next_monitoring": "Inspect every 3 days",
        "emergency_action": "Apply Streptocycline + Copper Oxychloride spray and prune infected lower foliage.",
        "farmer_tips": [
            "tamatar ko taar/laathi se baandhein",
            "neeche ke patte kaat dein",
            "copper + streptocycline spray karein"
        ],
        "faqs": [
            {
                "question": "Kya bacterial spot walei tamatar ko becha ja sakta hai?",
                "answer": "Halke daag wale tamatar khane yogya hote hain lekin market price kam milti hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Prune diseased lower leaves and stop overhead watering"],
            "today": ["Remove infected foliage", "Spray Copper Oxychloride (2.5g/L) + Streptocycline (0.1g/L)"],
            "next_3_days": ["Keep leaves completely dry", "Mulch soil around plants with dry straw"],
            "next_week": ["Repeat copper spray if rainy", "Apply Potassium & Calcium foliar fertilizer"],
            "monitoring_schedule": ["Inspect foliage every 3 days"],
            "emergency_conditions": ["Fruit scabbing spreading on over 15% of crop"],
            "expected_recovery": "10-14 Days",
            "success_indicators": ["No new brown spots on upper new leaves", "Fruit skin remains smooth"],
            "warning_signs": ["Rapid dropping of lower leaves", "Black crusty spots on young fruits"]
        }
    },
    {
        "id": "Tomato_Early_blight",
        "name": "Tomato Early Blight",
        "crop": "Tomato",
        "disease": "Tomato Early Blight",
        "scientific_name": "Alternaria solani",
        "disease_type": "Fungal",
        "severity": "Medium",
        "overview": "Early blight is a widespread fungal disease of tomatoes. It produces concentric target-like brown spots on leaves, stems, and fruit stem-ends.",
        "symptoms": [
            "Concentric target-board brown spots on leaves",
            "Yellowing around leaf spots",
            "Dark sunken leathery spots near fruit stem end",
            "Lower foliage turning yellow and dropping"
        ],
        "causes": [
            "Fungus Alternaria solani",
            "Soil-borne infected crop residue",
            "Warm humid weather and heavy dew"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": ["Temperature 24°C-29°C", "High humidity", "Wet foliage"],
        "spread_method": "Wind-borne spores, splashing water, insects, and contaminated tools.",
        "early_stage": "Small dark brown spots appear on oldest lower leaves.",
        "middle_stage": "Concentric rings develop inside spots; surrounding leaf turns yellow.",
        "severe_stage": "Defoliation moves up canopy; sunken dark rot on tomato fruit stems.",
        "organic_treatment": [
            "Copper Oxychloride (2.5g/L) spray",
            "Neem oil 5ml/L spray every 7 days"
        ],
        "biological_control": ["Trichoderma viride foliar spray (5g/L)"],
        "chemical_treatment": [
            "Mancozeb 75% WP (2g/L) or Chlorothalonil 75% WP (2g/L)",
            "Systemic: Difenoconazole 25% EC (0.5ml/L) or Azoxystrobin (1ml/L)"
        ],
        "recommended_fungicides": ["Mancozeb 75% WP", "Difenoconazole 25% EC", "Azoxystrobin 23% SC"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["NPK 19-19-19", "Potash"],
        "avoid_fertilizers": ["High Nitrogen without Potassium"],
        "micronutrients": ["Calcium", "Magnesium"],
        "watering_advice": "Water at plant base in the morning.",
        "soil_management": "Mulch soil and stake plants upright.",
        "weather_precautions": "Spray contact fungicides prior to humid cloudy periods.",
        "prevention": ["Rotate crops", "Prune lower leaves", "Mulch soil"],
        "do": ["Stake plants", "Remove infected lower leaves"],
        "dont": ["Do not irrigate foliage late evening"],
        "recovery_time": "10-12 Days",
        "yield_loss": "15-30%",
        "harvest_safety": "7-10 Days PHI",
        "nearby_crop_risk": "Moderate risk to potatoes",
        "next_monitoring": "Inspect every 3 days",
        "emergency_action": "Spray Difenoconazole or Mancozeb and prune lower affected leaves.",
        "farmer_tips": [
            "pattiya zameen se na chhuein",
            "mancozeb ka spray karein",
            "laathi se baandhein"
        ],
        "faqs": [
            {
                "question": "Kkya early blight se tamatar ko bachaya ja sakta hai?",
                "answer": "Haan, shuruaat mein bimar patte katkar mancozeb spray karne se paudha theek ho jata hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Remove blighted lower leaves", "Stake tomato plants"],
            "today": ["Prune bottom foliage up to 30cm", "Spray Mancozeb (2g/L) or Difenoconazole (0.5ml/L)"],
            "next_3_days": ["Keep leaves dry and check upper canopy"],
            "next_week": ["Re-apply fungicide if rain continues", "Feed Potassium nitrate"],
            "monitoring_schedule": ["Inspect every 3 days"],
            "emergency_conditions": ["If spots appear on stem joints or fruit bases"],
            "expected_recovery": "10-12 Days",
            "success_indicators": ["No target rings on new top foliage"],
            "warning_signs": ["Black leathery rot on green fruit stems"]
        }
    },
    {
        "id": "Tomato_Late_blight",
        "name": "Tomato Late Blight",
        "crop": "Tomato",
        "disease": "Tomato Late Blight",
        "scientific_name": "Phytophthora infestans",
        "disease_type": "Oomycete / Fungal-like",
        "severity": "Critical",
        "overview": "Late blight is a devastating disease of tomatoes causing rapid dark water-soaked rot on leaves, stems, and green fruits.",
        "symptoms": [
            "Large water-soaked dark green/black lesions on leaves",
            "White fuzzy growth on leaf undersides in wet weather",
            "Greasy brown firm rot on tomato fruits",
            "Rapid plant collapse"
        ],
        "causes": [
            "Phytophthora infestans",
            "Cool wet weather and high relative humidity (>90%)"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": ["Temperature 12°C-22°C", "High humidity", "Fog / Rain"],
        "spread_method": "Airborne spores carried by wind and fog.",
        "early_stage": "Pale dark green water-soaked spots on upper leaves.",
        "middle_stage": "Lesions turn purplish-black with white downy mold underneath; fruit rots.",
        "severe_stage": "Total plant defoliation and collapse.",
        "organic_treatment": ["Copper Oxychloride (3g/L) preventive spray"],
        "biological_control": ["Trichoderma viride foliar spray"],
        "chemical_treatment": [
            "Cymoxanil 8% + Mancozeb 64% (2g/L) or Metalaxyl + Mancozeb (2g/L)",
            "Dimethomorph 50% WP (1g/L)"
        ],
        "recommended_fungicides": ["Metalaxyl + Mancozeb (Ridomil Gold)", "Cymoxanil + Mancozeb", "Dimethomorph 50% WP"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Potassium Nitrate"],
        "avoid_fertilizers": ["Urea / High Nitrogen"],
        "micronutrients": ["Zinc", "Boron"],
        "watering_advice": "Stop all overhead watering.",
        "soil_management": "Ensure good drainage.",
        "weather_precautions": "Spray systemic fungicides before fog/rain events.",
        "prevention": ["Use resistant varieties", "Proper spacing"],
        "do": ["Spray systemic fungicide immediately at first local report"],
        "dont": ["Do not irrigate during foggy weather"],
        "recovery_time": "7-10 Days",
        "yield_loss": "Up to 100%",
        "harvest_safety": "14 Days PHI",
        "nearby_crop_risk": "Extreme risk to potato fields",
        "next_monitoring": "Inspect daily",
        "emergency_action": "Apply Metalaxyl + Mancozeb immediately and stop irrigation.",
        "farmer_tips": [
            "kohar aane par pehle hi ridomil gold spray karein",
            "paani bilkul rok dein",
            "sadhe tamatar phenk dein"
        ],
        "faqs": [
            {
                "question": "Late blight se tamatar kitni jaldi kharab hota hai?",
                "answer": "Nami wale mausam mein 3 se 5 din mein poori fasal sad sakti hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Halt irrigation", "Apply Metalaxyl + Mancozeb systemic spray"],
            "today": ["Stop watering", "Spray Metalaxyl + Mancozeb (2g/L)"],
            "next_3_days": ["Check leaf undersides for white mold daily"],
            "next_week": ["Re-apply Dimethomorph if wet weather continues"],
            "monitoring_schedule": ["Inspect daily"],
            "emergency_conditions": ["White fuzzy mold spreading on undersides"],
            "expected_recovery": "7-10 Days",
            "success_indicators": ["Black lesions turn dry and crisp"],
            "warning_signs": ["Foliage turning black overnight with rotting smell"]
        }
    },
    {
        "id": "Tomato_Leaf_Mold",
        "name": "Tomato Leaf Mold",
        "crop": "Tomato",
        "disease": "Tomato Leaf Mold",
        "scientific_name": "Passalora fulva / Cladosporium fulvum",
        "disease_type": "Fungal",
        "severity": "Medium",
        "overview": "Leaf mold primarily affects tomato foliage in humid conditions or greenhouses, causing pale yellow spots on leaf tops and olive-green velvet mold underneath.",
        "symptoms": [
            "Pale yellow spots on upper leaf surface",
            "Olive-green to brown velvety mold on leaf underside",
            "Leaves turn brown, curl, and dry up",
            "Rarely affects fruit directly"
        ],
        "causes": [
            "Fungus Passalora fulva",
            "High relative humidity (>85%) and poor ventilation"
        ],
        "affected_parts": ["Leaves", "Stems"],
        "favorable_conditions": ["Temperature 20°C-26°C", "Relative humidity >85%", "Stagnant humid air"],
        "spread_method": "Airborne spores spread by air currents and splashing rain.",
        "early_stage": "Pale light green to yellowish spots appear on upper leaf surface.",
        "middle_stage": "Olive-green velvet fungal growth covers leaf undersides corresponding to yellow spots.",
        "severe_stage": "Leaves dry up, wither, and drop, causing reduced fruit sizing.",
        "organic_treatment": [
            "Neem oil spray (5ml/L)",
            "Copper oxychloride (2.5g/L)"
        ],
        "biological_control": ["Trichoderma harzianum foliar spray"],
        "chemical_treatment": ["Spray Difenoconazole (0.5ml/L) or Mancozeb (2g/L) or Chlorothalonil (2g/L)"],
        "recommended_fungicides": ["Difenoconazole 25% EC", "Mancozeb 75% WP", "Chlorothalonil 75% WP"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK", "Potash"],
        "avoid_fertilizers": ["Excess Nitrogen"],
        "micronutrients": ["Magnesium", "Zinc"],
        "watering_advice": "Water at root zone. Improve airflow.",
        "soil_management": "Keep rows clean and weed-free.",
        "weather_precautions": "Increase greenhouse ventilation during humid periods.",
        "prevention": ["Prune dense canopy", "Use resistant tomato varieties"],
        "do": ["Prune foliage to increase air circulation", "Spray fungicide on undersides of leaves"],
        "dont": ["Do not overcrowd tomato plants"],
        "recovery_time": "10-14 Days",
        "yield_loss": "10-25%",
        "harvest_safety": "7 Days PHI",
        "nearby_crop_risk": "Low to non-tomato crops",
        "next_monitoring": "Inspect every 4 days",
        "emergency_action": "Prune lower dense branches to improve air flow and spray Difenoconazole.",
        "farmer_tips": [
            "pattiyo ke neeche spray zaroor karein",
            "hawa ka bahav achha rakhein",
            "peele patte hata dein"
        ],
        "faqs": [
            {
                "question": "Leaf mold patte ke neeche kyu hota hai?",
                "answer": "Fungus ko nami aur chhav pasand hai, isliye yeh patte ke neeche velvety fafundi banata hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Prune crowded lower foliage to increase air movement", "Spray leaf undersides"],
            "today": ["Prune dense leaves", "Spray Difenoconazole (0.5ml/L) targeting leaf undersides"],
            "next_3_days": ["Monitor air ventilation and lower canopy"],
            "next_week": ["Re-apply organic copper spray if humidity remains high"],
            "monitoring_schedule": ["Inspect leaf undersides every 4 days"],
            "emergency_conditions": ["Olive-green mold spreading to >30% foliage"],
            "expected_recovery": "10-14 Days",
            "success_indicators": ["Fungal velvet on undersides dries into powdery residue", "No new yellow spots"],
            "warning_signs": ["Widespread leaf curling and premature drying"]
        }
    },
    {
        "id": "Tomato_Septoria_leaf_spot",
        "name": "Tomato Septoria Leaf Spot",
        "crop": "Tomato",
        "disease": "Tomato Septoria Leaf Spot",
        "scientific_name": "Septoria lycopersici",
        "disease_type": "Fungal",
        "severity": "Medium",
        "overview": "Septoria leaf spot is a common fungal disease causing numerous small circular spots with dark borders and tan/grey centers containing black specks.",
        "symptoms": [
            "Numerous small circular spots (1-3mm) with dark brown borders",
            "Grey or tan centers in leaf spots",
            "Tiny black specks (pycnidia) inside spots",
            "Lower leaves turn yellow and drop off rapidly"
        ],
        "causes": [
            "Fungus Septoria lycopersici",
            "Infected plant debris in soil",
            "Warm wet conditions and rain splashing"
        ],
        "affected_parts": ["Leaves", "Stems"],
        "favorable_conditions": ["Temperature 20°C-25°C", "High humidity", "Wet leaf surface"],
        "spread_method": "Splashing rain, overhead irrigation, and garden tools.",
        "early_stage": "Tiny dark spots appear on oldest lower leaves near ground.",
        "middle_stage": "Spots grow to 3mm with grey centers and tiny black dots; leaf turns yellow.",
        "severe_stage": "Progressive upward defoliation leaving stems bare and fruit exposed to sunscald.",
        "organic_treatment": [
            "Copper Oxychloride (2.5g/L) spray",
            "Neem oil 5ml/L spray every 7 days"
        ],
        "biological_control": ["Trichoderma viride foliar spray"],
        "chemical_treatment": ["Spray Chlorothalonil (2g/L) or Mancozeb (2g/L) or Difenoconazole (0.5ml/L)"],
        "recommended_fungicides": ["Chlorothalonil 75% WP", "Mancozeb 75% WP", "Difenoconazole 25% EC"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK", "Potash"],
        "avoid_fertilizers": ["High Nitrogen"],
        "micronutrients": ["Magnesium", "Zinc"],
        "watering_advice": "Drip irrigate only.",
        "soil_management": "Mulch beds with straw to stop fungal spores splashing from soil.",
        "weather_precautions": "Spray fungicides before rainy spells.",
        "prevention": ["Mulch ground", "3-year crop rotation", "Stake plants"],
        "do": ["Mulch soil surface", "Prune lower leaves up to 30cm"],
        "dont": ["Do not leave infected leaves on the ground"],
        "recovery_time": "10-14 Days",
        "yield_loss": "15-30%",
        "harvest_safety": "7 Days PHI",
        "nearby_crop_risk": "Low to non-solanaceous crops",
        "next_monitoring": "Inspect every 3 days",
        "emergency_action": "Apply Chlorothalonil or Mancozeb spray and mulch ground.",
        "farmer_tips": [
            "pattiya zameen se na lagne dein",
            "bhuusa (straw) ki mulch lagayein",
            "mancozeb ka spray karein"
        ],
        "faqs": [
            {
                "question": "Septoria spot tamatar ke fal ko kharab karta hai?",
                "answer": "Yeh fal par seedha nahi aata par patte girne se tamatar dhoop mein jhalas jata hai."
            }
        ],
        "action_plan": {
            "immediate_action": ["Remove infected lower leaves", "Apply thick organic mulch over soil"],
            "today": ["Prune bottom yellow leaves", "Mulch bed", "Spray Chlorothalonil or Mancozeb (2g/L)"],
            "next_3_days": ["Check middle leaves for new circular grey-center spots"],
            "next_week": ["Repeat protective fungicide spray if rain occurs"],
            "monitoring_schedule": ["Inspect foliage every 3 days"],
            "emergency_conditions": ["Leaf spots spreading rapidly up to middle canopy"],
            "expected_recovery": "10-14 Days",
            "success_indicators": ["Upper green leaves remain clean without circular spots"],
            "warning_signs": ["Lower half of plant becoming completely defoliated"]
        }
    },
    {
        "id": "Tomato_Spider_mites_Two_spotted_spider_mite",
        "name": "Tomato Two-Spotted Spider Mites",
        "crop": "Tomato",
        "disease": "Tomato Two-Spotted Spider Mites",
        "scientific_name": "Tetranychus urticae",
        "disease_type": "Pest / Mite Infestation",
        "severity": "Medium",
        "overview": "Two-spotted spider mites are microscopic sap-sucking arachnids. They cause fine yellow stippling/speckling on leaves and produce fine silk webbing on foliage in hot dry weather.",
        "symptoms": [
            "Fine yellow stippling or dot speckling on leaves",
            "Leaves turn bronze, greyish, or dry brown",
            "Fine silk webbing on leaf undersides and stems",
            "Tiny moving red/yellow specks under leaf"
        ],
        "causes": [
            "Microscopic mite Tetranychus urticae",
            "Hot, dry, and dusty weather conditions",
            "Overuse of broad-spectrum insecticides killing natural predators"
        ],
        "affected_parts": ["Leaves", "Stems"],
        "favorable_conditions": ["Temperature >30°C", "Low humidity (<50%)", "Dusty conditions"],
        "spread_method": "Wind currents, silk webbing silk-threading, and contact with farm workers.",
        "early_stage": "Light yellow speckling/stippling on leaf upper surface.",
        "middle_stage": "Speckling intensifies; bronze discoloration and fine webbing appear underneath.",
        "severe_stage": "Leaves dry out completely; heavy webbing covers plant tips; defoliation.",
        "organic_treatment": [
            "Spray Neem oil 10000 ppm (5ml/L) with potassium soap",
            "High pressure water spray on leaf undersides to wash off mites"
        ],
        "biological_control": ["Release predatory mites Phytoseiulus persimilis or Chrysoperla carnea"],
        "chemical_treatment": [
            "Acaricide / Miticide spray: Abamectin 1.9% EC (0.5ml/L) or Spiromesifen 22.9% SC (1ml/L) or Propargite 57% EC (2ml/L)"
        ],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Abamectin 1.9% EC", "Spiromesifen 22.9% SC (Oberon)", "Propargite 57% EC"],
        "recommended_fertilizers": ["Balanced NPK", "Potassium"],
        "avoid_fertilizers": ["Excessive Nitrogen"],
        "micronutrients": ["Sulfur foliar spray"],
        "watering_advice": "Maintain good soil moisture and spray overhead water occasionally to raise micro-humidity.",
        "soil_management": "Keep field borders moist and free of dusty weeds.",
        "weather_precautions": "Be extra vigilant during hot dry heatwaves.",
        "prevention": ["Avoid dusty roadsides", "Preserve natural predatory insects"],
        "do": ["Spray miticide on undersides of leaves", "Spray water to increase humidity"],
        "dont": ["Do not use pyrethroid insecticides which increase mite reproduction"],
        "recovery_time": "7-10 Days",
        "yield_loss": "15-35%",
        "harvest_safety": "7-14 Days PHI depending on acaricide used",
        "nearby_crop_risk": "High risk to beans, brinjal, and peppers",
        "next_monitoring": "Inspect undersides of leaves every 2-3 days",
        "emergency_action": "Spray Abamectin or Spiromesifen targeting leaf undersides immediately.",
        "farmer_tips": [
            "patte ke neeche paani ka teez dhaar maarein",
            "oberon (spiromesifen) ya abamectin spray karein",
            "dhoop aur dhool se bachayein"
        ],
        "faqs": [
            {
                "question": "Spider mite aur sadharan keede mein kya antar hai?",
                "answer": "Spider mite bahut chhote spider jaise hote hain jo patte ke neeche baarik jaala (webbing) banate hain."
            }
        ],
        "action_plan": {
            "immediate_action": ["Spray water stream on leaf undersides to knock off mites", "Apply miticide"],
            "today": ["Spray Spiromesifen (1ml/L) or Abamectin (0.5ml/L) targeting leaf undersides", "Wash off dust from field borders"],
            "next_3_days": ["Inspect leaf undersides using hand lens for live moving mites"],
            "next_week": ["Repeat miticide spray with different mode of action if live mites persist"],
            "monitoring_schedule": ["Inspect leaf undersides every 3 days"],
            "emergency_conditions": ["Silk webbing visible over plant growing tips"],
            "expected_recovery": "7-10 Days",
            "success_indicators": ["No new yellow stippling on young leaves", "Webbing drops away"],
            "warning_signs": ["Leaves turning bronze and crispy dry"]
        }
    },
    {
        "id": "Tomato__Target_Spot",
        "name": "Tomato Target Spot",
        "crop": "Tomato",
        "disease": "Tomato Target Spot",
        "scientific_name": "Corynespora cassiicola",
        "disease_type": "Fungal",
        "severity": "Medium",
        "overview": "Target spot affects leaves, stems, and fruits of tomato. It produces brown spots with light brown centers and dark brown margins, expanding into target-board shapes.",
        "symptoms": [
            "Brown circular spots with pale centers and dark concentric rings",
            "Yellow halo surrounding leaf spots",
            "Sunken dark brown spots on green/ripe tomato fruit",
            "Foliar blighting and leaf drop"
        ],
        "causes": [
            "Fungus Corynespora cassiicola",
            "High humidity and warm temperatures",
            "Infected plant debris"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": ["Temperature 20°C-28°C", "Relative humidity >80%", "Free moisture on leaves"],
        "spread_method": "Airborne spores and rain splash.",
        "early_stage": "Small pinpoint brown flecks on lower leaves.",
        "middle_stage": "Flecks enlarge to circular target-like spots with yellow halos.",
        "severe_stage": "Spots coalesce leading to leaf collapse and fruit pitting.",
        "organic_treatment": ["Copper Oxychloride (2.5g/L) spray", "Neem oil 5ml/L spray"],
        "biological_control": ["Trichoderma harzianum foliar application"],
        "chemical_treatment": ["Chlorothalonil (2g/L) or Azoxystrobin (1ml/L) or Difenoconazole (0.5ml/L) spray"],
        "recommended_fungicides": ["Chlorothalonil 75% WP", "Azoxystrobin 23% SC", "Difenoconazole 25% EC"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK", "Potash"],
        "avoid_fertilizers": ["Excess Nitrogen"],
        "micronutrients": ["Calcium", "Zinc"],
        "watering_advice": "Drip irrigation only.",
        "soil_management": "Keep soil covered with organic mulch.",
        "weather_precautions": "Spray protective fungicides before humid wet spells.",
        "prevention": ["Crop rotation", "Stake tomato vines", "Clean debris"],
        "do": ["Stake plants for aeration", "Remove infected foliage"],
        "dont": ["Do not overhead irrigate"],
        "recovery_time": "10-14 Days",
        "yield_loss": "15-30%",
        "harvest_safety": "7 Days PHI",
        "nearby_crop_risk": "Moderate risk to papaya and cucumber",
        "next_monitoring": "Inspect every 4 days",
        "emergency_action": "Spray Azoxystrobin or Chlorothalonil and prune infected leaves.",
        "farmer_tips": [
            "azoxystrobin ya mancozeb ka spray karein",
            "paudho ke beech mein jagah rakhein",
            "drip se paani dein"
        ],
        "faqs": [
            {
                "question": "Target spot se kaise bachayein?",
                "answer": "Fasal mein hawa ka bahav achha rakhein aurazoxystrobin fungicide ka spray karein."
            }
        ],
        "action_plan": {
            "immediate_action": ["Prune spotted lower foliage", "Ensure good plant spacing"],
            "today": ["Remove infected leaves", "Spray Azoxystrobin (1ml/L) or Chlorothalonil (2g/L)"],
            "next_3_days": ["Check middle foliage for new circular target spots"],
            "next_week": ["Re-apply Difenoconazole if symptoms persist"],
            "monitoring_schedule": ["Inspect foliage every 4 days"],
            "emergency_conditions": ["Sunken dark pits appearing on green fruits"],
            "expected_recovery": "10-14 Days",
            "success_indicators": ["New leaves grow without brown target spots"],
            "warning_signs": ["Extensive yellowing and leaf loss in mid-canopy"]
        }
    },
    {
        "id": "Tomato__Tomato_YellowLeaf__Curl_Virus",
        "name": "Tomato Yellow Leaf Curl Virus",
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "scientific_name": "Begomovirus (TYLCV)",
        "disease_type": "Viral",
        "severity": "Critical",
        "overview": "TYLCV is a devastating viral disease transmitted solely by whiteflies. It causes severe leaf curling, stunting, yellowing, and near-total loss of fruit production if infected early.",
        "symptoms": [
            "Upward curling and cupping of young leaves",
            "Yellowing (chlorosis) of leaf margins and veins",
            "Severe plant stunting and bushy dwarf appearance",
            "Flower dropping and failure to set fruit"
        ],
        "causes": [
            "Tomato Yellow Leaf Curl Virus (Begomovirus)",
            "Transmitted by Whitefly vector (Bemisia tabaci)",
            "Hot dry weather favoring whitefly explosion"
        ],
        "affected_parts": ["Foliage", "Shoots", "Flowers"],
        "favorable_conditions": ["Temperature 28°C-38°C", "High whitefly populations", "Dry weather"],
        "spread_method": "Transmitted strictly by whiteflies (Bemisia tabaci) feeding on plant sap.",
        "early_stage": "Young top leaves exhibit slight upward curling and yellowing between veins.",
        "middle_stage": "Shoots become severely stunted; leaves cup upward like spoons with bright yellow edges.",
        "severe_stage": "Plant stops growing completely; flowers drop; no new fruit formation.",
        "organic_treatment": [
            "Neem oil 10000 ppm (5ml/L) + Sticky yellow traps (20 per acre) to catch whiteflies",
            "Spray Verticillium lecanii or Beauveria bassiana bio-insecticide (5g/L)"
        ],
        "biological_control": ["Release Chrysoperla carnea predators", "Yellow sticky traps"],
        "chemical_treatment": [
            "Control Whitefly Vector: Imidacloprid 17.8% SL (0.5ml/L) or Thiamethoxam 25% WG (0.3g/L) or Acetamiprid 20% SP (0.5g/L) or Spirotetramat 15.31% OD (1ml/L)"
        ],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Imidacloprid 17.8% SL", "Thiamethoxam 25% WG", "Acetamiprid 20% SP"],
        "recommended_fertilizers": ["Micronutrient mixture", "Potassium Nitrate"],
        "avoid_fertilizers": ["Excessive Urea"],
        "micronutrients": ["Zinc", "Boron", "Magnesium"],
        "watering_advice": "Maintain adequate soil moisture to reduce drought stress.",
        "soil_management": "Use silver-colored reflective mulch to repel whiteflies.",
        "weather_precautions": "Deploy yellow traps before hot dry summer periods.",
        "prevention": [
            "Plant TYLCV-resistant tomato hybrids",
            "Use 40-mesh insect net in nurseries",
            "Install yellow sticky traps early"
        ],
        "do": ["Uproot and bury severely infected stunted plants early", "Control whiteflies aggressively"],
        "dont": ["Do not leave viral infected plants in field to spread virus"],
        "recovery_time": "Viruses cannot be cured; vector control prevents new infection (14-21 Days for vector control)",
        "yield_loss": "50-100% if infected within 4 weeks of planting",
        "harvest_safety": "7-14 Days PHI for systemic insecticides",
        "nearby_crop_risk": "Extreme risk to chilli, brinjal, and papaya",
        "next_monitoring": "Inspect yellow sticky traps and tops every 2 days",
        "emergency_action": "Uproot infected dwarf plants, deploy yellow sticky traps, and spray Thiamethoxam or Imidacloprid immediately to kill whiteflies.",
        "farmer_tips": [
            "safed makkhi (whitefly) ko marne ke liye imidacloprid spray karein",
            "peele chipchipe card (yellow sticky trap) lagayein",
            "beemar dwarf paudhe ufaad kar fek dein"
        ],
        "faqs": [
            {
                "question": "Kya virus wale paudhe ko dawayi se theek kiya ja sakta hai?",
                "answer": "Nahi, virus ka koi ilaj nahi hai. Safed makkhi ko maarkar baaki khet ko bachaya jata hai."
            }
        ],
        "action_plan": {
            "immediate_action": [
                "Remove and destroy severely stunted yellow-curled plants",
                "Install 20 yellow sticky traps per acre"
            ],
            "today": [
                "Uproot viral infected dwarf plants",
                "Set up yellow sticky traps to catch whiteflies",
                "Spray Thiamethoxam 25% WG (0.3g/L) or Imidacloprid (0.5ml/L)"
            ],
            "next_3_days": [
                "Check yellow traps for trapped whiteflies",
                "Inspect growing tips of healthy plants for leaf curling"
            ],
            "next_week": [
                "Rotate systemic insecticide with Spirotetramat or Acetamiprid if whiteflies persist",
                "Apply micronutrient foliar spray to boost uninfected plants"
            ],
            "monitoring_schedule": ["Inspect yellow traps and plant tips every 2 days"],
            "emergency_conditions": ["Whiteflies flying in swarms when plants are shaken"],
            "expected_recovery": "Vector Control in 7-10 Days (Uninfected plants protected)",
            "success_indicators": ["Whitefly population drops to near zero", "New shoots grow straight and green"],
            "warning_signs": ["Spreading upward leaf curling on surrounding plants"]
        }
    },
    {
        "id": "Tomato__Tomato_mosaic_virus",
        "name": "Tomato Mosaic Virus",
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "scientific_name": "Tobamovirus (ToMV)",
        "disease_type": "Viral",
        "severity": "High",
        "overview": "Tomato Mosaic Virus causes mottled light and dark green patches on leaves, fern-like leaf distortion, and uneven fruit ripening.",
        "symptoms": [
            "Mottled light green and dark green mosaic pattern on leaves",
            "Shoots and leaves distorted into fern-like shapes",
            "Internal brown necrosis in fruit walls",
            "Uneven fruit ripening"
        ],
        "causes": [
            "Pathogen Tomato Mosaic Virus (ToMV)",
            "Mechanical transmission via hands, clothing, tools, and tobacco products",
            "Contaminated seed stock"
        ],
        "affected_parts": ["Leaves", "Stems", "Fruit"],
        "favorable_conditions": ["Warm temperatures 20°C-30°C", "Frequent handling of plants"],
        "spread_method": "Extremely stable virus spread mechanically by hands, tools, clothes, and seed.",
        "early_stage": "Light green and dark green mottling on young upper leaves.",
        "middle_stage": "Leaves become narrow and puckered like fern leaves; plant growth slows.",
        "severe_stage": "Severe stunting, internal brown rings in fruits, and severe yield reduction.",
        "organic_treatment": [
            "Spray Milk solution (20% skimmed milk in water) to inhibit mechanical viral transmission",
            "Apply Neem oil (5ml/L)"
        ],
        "biological_control": ["Information unavailable"],
        "chemical_treatment": [
            "No chemical cure exists for plant viruses.",
            "Sanitize tools with 10% trisodium phosphate (TSP) or 20% reconstituted non-fat dry milk solution."
        ],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["Balanced NPK", "Potassium Sulfate"],
        "avoid_fertilizers": ["Excessive Nitrogen"],
        "micronutrients": ["Zinc", "Boron"],
        "watering_advice": "Water normally at soil level.",
        "soil_management": "Avoid working in soil when wet.",
        "weather_precautions": "Keep tools sanitized during heat/growth phases.",
        "prevention": [
            "Use certified virus-free seeds",
            "Wash hands with soap/milk before handling plants",
            "Do not smoke or use tobacco near tomato plants"
        ],
        "do": ["Wash hands thoroughly before farm work", "Disinfect pruning shears"],
        "dont": ["Do not touch healthy plants after touching mosaic-infected plants"],
        "recovery_time": "No cure; preventive hygiene protects healthy crop",
        "yield_loss": "20-50%",
        "harvest_safety": "Safe for consumption, but fruit quality is reduced",
        "nearby_crop_risk": "High risk to pepper, tobacco, and petunia crops",
        "next_monitoring": "Inspect weekly",
        "emergency_action": "Uproot infected mosaic plants, wash hands with soap/milk, and sanitize all tools.",
        "farmer_tips": [
            "bimar paudhe ko hath lagane ke baad sabun se hath dhoyein",
            "tombaku (tobacco) ka sevan khet mein na karein",
            "doodh (milk spray) se viral spread kam hota hai"
        ],
        "faqs": [
            {
                "question": "Kya mosaic virus insano ke liye khatarnak hai?",
                "answer": "Nahi, yeh sirf paudho ka virus hai. Insano par koi asar nahi hota."
            }
        ],
        "action_plan": {
            "immediate_action": [
                "Isolate mosaic-patterned plants and remove carefully without touching healthy neighbors",
                "Wash hands with soap or milk solution"
            ],
            "today": [
                "Uproot mosaic-infected plants",
                "Disinfect all cutting tools with 10% trisodium phosphate or milk solution",
                "Wash workers' clothes before re-entering field"
            ],
            "next_3_days": [
                "Monitor surrounding plants for mottled leaf symptoms"
            ],
            "next_week": [
                "Apply potassium foliar spray to strengthen healthy plants"
            ],
            "monitoring_schedule": ["Inspect field weekly"],
            "emergency_conditions": ["Mosaic symptoms spreading along plant rows"],
            "expected_recovery": "No cure for infected plants; healthy plants remain protected",
            "success_indicators": ["New leaves on healthy plants remain solid green"],
            "warning_signs": ["Fern-like leaf distortion spreading to adjacent plants"]
        }
    },
    {
        "id": "Tomato_healthy",
        "name": "Tomato Healthy",
        "crop": "Tomato",
        "disease": "Healthy Crop",
        "scientific_name": "Solanum lycopersicum",
        "disease_type": "None",
        "severity": "None",
        "overview": "The tomato crop is healthy, exhibiting dark green foliage, sturdy stems, and abundant flowers and fruit development.",
        "symptoms": ["No disease symptoms present", "Vibrant green leaves and sturdy growth"],
        "causes": ["Good cultural management and balanced nutrition"],
        "affected_parts": ["None"],
        "favorable_conditions": ["Temperature 20°C-28°C", "Moderate moisture", "Full sun"],
        "spread_method": "None",
        "early_stage": "Healthy seedling growth.",
        "middle_stage": "Active flowering and fruit setting.",
        "severe_stage": "None",
        "organic_treatment": ["Preventive Neem oil (3ml/L) spray every 14 days"],
        "biological_control": ["Trichoderma viride root drenching"],
        "chemical_treatment": ["None required"],
        "recommended_fungicides": ["Information unavailable"],
        "recommended_bactericides": ["Information unavailable"],
        "recommended_insecticides": ["Information unavailable"],
        "recommended_fertilizers": ["NPK 19-19-19", "Calcium Nitrate"],
        "avoid_fertilizers": ["Excessive Nitrogen"],
        "micronutrients": ["Boron for flower retention", "Calcium for blossom end rot prevention"],
        "watering_advice": "Provide steady drip irrigation to prevent blossom end rot.",
        "soil_management": "Mulch soil and stake vines.",
        "weather_precautions": "Protect from heavy rain storms with proper drainage.",
        "prevention": ["Maintain staking, weeding, and drip irrigation"],
        "do": ["Keep lower leaves pruned 20cm above soil", "Stake vines securely"],
        "dont": ["Do not let fruits touch bare soil"],
        "recovery_time": "Already healthy",
        "yield_loss": "0%",
        "harvest_safety": "Safe for regular harvest",
        "nearby_crop_risk": "Low",
        "next_monitoring": "Inspect every 7 days",
        "emergency_action": "None required.",
        "farmer_tips": [
            "tamatar ko laathi se baandh kar rakhein",
            "drip se niyamit paani dein",
            "boron aur calcium spray karein"
        ],
        "faqs": [
            {
                "question": "Tamatar ko kitna paani dena chahiye?",
                "answer": "Drip se rozana ya 1 din chhodkar halki sinchai karein taaki mitti mein sami bani rahe."
            }
        ],
        "action_plan": {
            "immediate_action": ["Maintain regular irrigation and staking routine"],
            "today": ["Perform regular field walk", "Verify drip emitters"],
            "next_3_days": ["Prune bottom yellowing leaves touching ground"],
            "next_week": ["Foliar spray Boron + Calcium for fruit development"],
            "monitoring_schedule": ["Inspect weekly"],
            "emergency_conditions": ["None"],
            "expected_recovery": "Already Healthy",
            "success_indicators": ["Plump firm green/red fruits", "Deep green lush leaves"],
            "warning_signs": ["Any yellow spots or whitefly sightings"]
        }
    }
]

# Build JSON structure
full_kb = {
    "version": "2.0",
    "last_updated": "2026-07-18",
    "crops_supported": ["tomato", "potato", "pepper", "all"],
    "diseases": diseases_data,
    "fallback": {
        "message": "Iska exact match knowledge base mein nahi mila. AI Crop Doctor dwara raye di ja rahi hai.",
        "action": "call_sarvam_ai"
    }
}

os.makedirs(os.path.dirname(KB_PATH_1), exist_ok=True)
os.makedirs(os.path.dirname(KB_PATH_2), exist_ok=True)

with open(KB_PATH_1, "w", encoding="utf-8") as f:
    json.dump(full_kb, f, indent=2, ensure_ascii=False)

with open(KB_PATH_2, "w", encoding="utf-8") as f:
    json.dump(full_kb, f, indent=2, ensure_ascii=False)

print(f"Successfully generated Knowledge Base with {len(diseases_data)} entries!")
