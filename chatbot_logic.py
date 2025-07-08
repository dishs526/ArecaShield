import re
import json
import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import math

# --- 1. Enhanced Knowledge Base (Your updated data with schemes) ---
enhanced_knowledge_base = {
    'greeting': {
        'keywords': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste'],
        'responses': [
            'Hello! How can I assist you with your arecanut farming today?',
            'Hi there! Welcome back. What farming questions do you have?',
            'Greetings! I am ready to help. What\'s on your mind regarding arecanut?'
        ]
    },
    'thanks': {
        'keywords': ['thank you', 'thanks', 'appreciate', 'good job', 'well done', 'ok thanks'],
        'responses': [
            'You\'re welcome! I\'m glad I could help.',
            'No problem at all! Feel free to ask if you have more questions.',
            'My pleasure! Happy farming!'
        ]
    },
    'disease': {
        'keywords': ['disease', 'sick', 'spots', 'yellow', 'brown', 'fungus', 'pest', 'infection',
                     'bud rot', 'stem bleeding', 'cracking', 'mahali', 'koleroga', 'anabe',
                     'root rot', 'leaf disease', 'bud borer', 'stem cracking',
                     'wilt', 'rots', 'dieback', 'lesions', 'gummosis', 'infestation', 'symptoms'],
        'responses': [
            'I can diagnose and provide detailed treatment protocols for various arecanut diseases. Please specify the disease name or describe symptoms in detail.',
            'To help you with disease, please tell me the specific disease name (e.g., bud rot, stem bleeding) or describe the symptoms.'
        ],
        'diseases': {
            'bud_rot': 'Crown/bud rot - Critical disease causing rotting of growing point, foul smell, yellowing of central leaves, and potential tree death.',
            'stem_bleeding': 'Reddish-brown patches on stem with gum exudation, internal tissue decay. Fatal if untreated.',
            'stem_cracking': 'Longitudinal cracks on stem due to water stress, nutrient imbalance, or environmental factors. It often indicates internal stress or nutritional deficiencies.',
            'mahali_koleroga': 'Nut fall disease - Premature dropping of young nuts, especially during monsoon season.',
            'anabe_roga': 'Inflorescence rot causing flower and young nut dropping, reducing yield significantly.',
            'fruit_rot': 'Post-harvest fungal infection causing fruit deterioration and storage losses.',
            'yellow_leaf_disease': 'Lethal disease causing yellowing of leaves, transmitted by insect vectors.',
            'root_rot': 'Fungal infection of root system causing wilting and eventual tree death.',
            'bud_borer': 'Insect pest that bores into the tender unopened leaves, causing holes and damage. Can lead to bud rot if not controlled.'
        }
    },
    'pesticide': {
        'keywords': ['pesticide', 'spray', 'fungicide', 'insecticide', 'chemical', 'treatment', 'dosage', 'application', 'weather spray', 'pest control', 'aphids', 'mites', 'mealybugs'],
        'responses': [
            'To recommend precise pesticide applications, I need current weather conditions. Please provide temperature, humidity, wind speed, and rainfall data.',
            'For effective and safe pesticide application, weather conditions are crucial. What are your current weather parameters?'
        ],
        'required_params': ['temperature', 'humidity', 'rainfall', 'windSpeed']
    },
    'fertilizer': {
        'keywords': ['fertilizer', 'nutrient', 'feeding', 'growth', 'npk', 'manure', 'organic', 'dosage', 'application', 'nutrition', 'soil', 'ph', 'compost', 'urea', 'dap', 'potash'],
        'responses': [
            'To calculate optimal fertilizer recommendations, I need soil conditions (pH, organic matter) and current weather (temperature, humidity, rainfall). Please provide these details.',
            'Precision fertilizer application depends on multiple factors. What are your soil test results and current weather conditions?'
        ],
        'required_params': ['temperature', 'humidity', 'rainfall', 'pH', 'organicMatter']
    },
    'harvest': {
        'keywords': ['harvest', 'ready', 'ripe', 'color', 'picking', 'mature', 'timing', 'prediction', 'market', 'when to harvest', 'harvest date', 'fruit maturity', 'are nuts ready', 'yield', 'best month to harvest', 'harvest season'],
        'responses': [
            'To predict optimal harvest timing, I need the current fruit maturity percentage, temperature, rainfall, and humidity. Can you provide these details?',
            'Harvest prediction requires fruit development stage, weather data, and tree age. Please provide these parameters for accurate timing.',
            'Arecanut harvesting usually starts from the 7th or 8th year after planting. The peak harvesting season in most regions of India is from **September to December/January**. Harvesting typically involves climbing the palm and detaching ripe bunches.'
        ],
        'required_params': ['fruitMaturity', 'temperature', 'rainfall', 'humidity']
    },
    'weather': {
        'keywords': ['weather', 'temperature', 'humidity', 'rain', 'wind', 'climate', 'season', 'forecast', 'today\'s weather'],
        'responses': [
            'Weather conditions significantly impact all arecanut farming operations. I can provide weather-based recommendations for spraying, fertilizing, and other activities. What specific weather data (temperature, humidity, rainfall, wind speed) do you want to know about?',
            'Current weather analysis helps optimize farming decisions. What specific weather-related guidance do you need?'
        ]
    },
    'general': {
        'keywords': ['growing', 'cultivation', 'care', 'tips', 'help', 'spacing', 'management', 'arecanut', 'palm', 'plant', 'info', 'general advice', 'how to grow', 'arecanut success factors'],
        'responses': [
            'I can provide general information on arecanut cultivation, care, and management practices. What specific aspect are you interested in?',
            'Arecanut farming involves several key practices including selecting good planting material, proper site selection (climate & soil), irrigation, timely manuring, pest and disease management, and appropriate harvesting methods.',
            'Key factors for arecanut success include proper spacing (2.7m x 2.7m), efficient irrigation, integrated pest control, balanced nutrition, and timely operations. Are you looking for information on specific aspects like planting, climate, or pest control?'
        ]
    },
    'arecanut_info': {
        'keywords': ['arecanut plant', 'arecanut information', 'palm tree facts', 'scientific name', 'areca nut', 'betel nut', 'general plant info', 'about arecanut'],
        'responses': [
            'The arecanut palm (Areca catechu L.) is a tall, slender palm cultivated for its nut, which is chewed by a large section of the people in Southeast Asian and Pacific countries. It is often referred to as "betel nut" because it\'s commonly chewed with betel leaves. It is a major commercial crop in many parts of India, especially in Karnataka, Kerala, and Assam.',
            'Arecanut palms can grow up to 20 meters tall, with a straight, unbranched stem marked with ring-like leaf scars. The leaves are large, pinnate, and form a crown at the top. The nuts are typically green when raw, turning yellow or orange-red when ripe.'
        ]
    },
    'climate_soil': {
        'keywords': ['climate', 'soil', 'temperature range', 'rainfall', 'ideal soil', 'soil type', 'altitude', 'best climate', 'pH for arecanut', 'climate requirement', 'soil requirement'],
        'responses': [
            'Arecanut thrives in humid tropical and sub-tropical areas. It prefers temperatures between 14°C and 36°C, but can tolerate up to 40°C. Prolonged temperatures below 10°C or above 40°C are detrimental. It requires high humidity.',
            'Annual rainfall ranging from 750 mm to 4,500 mm is suitable, but irrigation is essential during dry periods. Optimal altitude is generally below 1000m MSL. Strong winds can cause heavy shedding of nuts and toppling of palms, so windbreaks are often necessary.',
            'For soil, arecanut prefers deep, well-drained, fertile soils. Gravelly laterite soils, red clay type, fertile clay loam, red loam, and alluvial soils are considered suitable. It performs best in soils with a pH ranging from 6.0 to 7.0. Avoid sticky clay, sandy, brackish, and calcareous soils, as well as areas with high water tables or prone to waterlogging.'
        ]
    },
    'propagation': {
        'keywords': ['propagation', 'seeds', 'seedling', 'nursery', 'planting material', 'mother palm', 'seed nut', 'how to plant', 'raising seedlings'],
        'responses': [
            'Arecanut is primarily propagated through seeds. The key steps involve selecting superior mother palms, choosing healthy seed nuts, and then raising seedlings in a two-stage nursery system (primary and secondary nurseries).',
            'To select a mother palm: Choose palms that are early bearing (around 5-6 years), regular bearers, produce at least 5-6 bunches annually, have large nuts (over 35g), and are free from pests and diseases. Nuts from the middle bunches are generally preferred as seed nuts.',
            'Seed nuts should be fully ripened, sinking or floating vertically in water (not horizontally). They are sown 5-6 cm apart, with the stalk end facing upwards, in sand beds under partial shade. Germination takes about 40-50 days.',
            'After 2-3 leaves emerge (around 90 days), the sprouts are transplanted to a secondary nursery. Here, they are spaced 30x30 cm apart or planted in polythene bags. Seedlings are kept in the secondary nursery for 12-18 months. For main field planting, select vigorous seedlings with 5 or more leaves, good height, and maximum girth.'
        ]
    },
    'planting': {
        'keywords': ['planting', 'spacing', 'pits', 'transplanting', 'main field', 'planting time', 'shade for young palms', 'sun scorching', 'how to plant arecanut', 'when to plant', 'best time to plant'],
        'responses': [
            'The recommended spacing for arecanut is generally **2.7 meters x 2.7 meters (9x9 feet)**. This allows for proper light penetration and air circulation.',
            'Planting pits should be prepared in advance. The ideal size is 90 cm x 90 cm x 90 cm (length, width, depth) for deep, well-drained soils, or 60 cm x 60 cm x 60 cm for heavy soils. These pits should be refilled with a mixture of topsoil, compost, and farmyard manure (FYM).',
            'The best time for planting in the main field is with the onset of the monsoon, usually **May-June**. In areas experiencing severe South-West monsoon or waterlogging, planting can be done later in September-October after the monsoon rains subside.',
            'Young arecanut palms are very susceptible to sun scorching. It is crucial to provide shade to the transplanted seedlings. This can be done by covering them with areca leaves, bamboo frames, or by intercropping with shade-providing crops like banana.'
        ]
    },
    'irrigation': {
        'keywords': ['irrigation', 'watering', 'water requirement', 'drip irrigation', 'dry spell', 'water logging', 'how much water', 'when to water'],
        'responses': [
            'Arecanut is very sensitive to moisture stress, especially during dry periods (typically November to May in the West Coast of India). Consistent irrigation is critical for good yield and palm health.',
            '**Traditional Irrigation:** If using flood irrigation, each palm may require about 175 liters of water per irrigation. The frequency depends on soil type and climate: generally once every 7-8 days in November-December, every 6 days in February, and every 3-5 days in March-April-May.',
            '**Drip Irrigation:** This is highly efficient and recommended. Drip irrigation can save about 44% of water compared to flood irrigation. Each palm requires approximately 16-20 liters of water per day through drip emitters, distributed evenly.',
            '**Waterlogging Prevention:** Ensure proper drainage by having channels at least 75 cm deep. Arecanut palms cannot tolerate waterlogged conditions, which can lead to root rot and other diseases.'
        ]
    },
    'manuring': {
        'keywords': ['manuring', 'fertilizers', 'nutrients', 'npk application', 'organic manure', 'compost', 'fyM', 'green leaf', 'application method', 'fertilizer dose', 'how to fertilize'],
        'responses': [
            'For **bearing arecanut palms (5 years and above)**, an annual application of 10-15 kg of Farm Yard Manure (FYM) or green leaf compost is recommended per palm.',
            'In addition to organic manure, chemical fertilizers are also essential. The recommended dose per palm per year is: **100g Nitrogen (N), 40g Phosphorus (P2O5), and 140g Potassium (K2O)**.',
            'This chemical dose can be achieved using approximately: 220g Urea (for N), 200g Rock Phosphate (for P2O5), and 230g Muriate of Potash (for K2O).',
            'For **young palms (less than 5 years)**, apply half the recommended chemical dose, gradually increasing to the full dose as the palm matures.',
            '**Application Method & Timing:** Under irrigated conditions, apply fertilizers in **two split doses**: the first during September-October (post-monsoon) and the second in February (pre-summer). Under rainfed conditions, the second dose is applied in March-April after the summer rains. Apply fertilizers in circular basins (0.75-1.0m radius, 15-20cm deep) around the base of the tree and lightly cover with soil.'
        ]
    },
    'intercropping': {
        'keywords': ['intercropping', 'mixed cropping', 'companion crops', 'additional income', 'banana', 'pepper', 'cocoa', 'vanilla', 'arecanut intercrop', 'profit from intercropping', 'tell about intercropping', 'what is intercropping'],
        'responses': [
            'Intercropping is a highly beneficial practice in arecanut gardens. It helps maximize land utilization, improves soil health through diversified root systems and organic matter, and provides additional income for farmers.',
            '**Suitable Intercrops:** Many crops can be successfully intercropped with arecanut, depending on climate and market. Popular choices include:',
            '• **Banana:** Can be planted simultaneously between four arecanut palms, providing shade for young palms and early income.',
            '• **Pineapple:** A good ground-level crop that utilizes space efficiently.',
            '• **Black Pepper:** Can be planted on the northern side of arecanut palms (about 75cm distance) once the palms are 6-8 years old, using the arecanut trunk as support.',
            '• **Cocoa:** Thrives in the shade provided by mature arecanut palms and is a high-value crop.',
            '• **Coffee and Vanilla:** Also good choices in specific climatic zones.',
            '• **Citrus varieties:** Can also be grown successfully.',
            'High-density multi-species cropping systems combining crops like banana, pepper, and cocoa are very profitable in coastal regions with good irrigation.'
        ]
    },
    'government_schemes': {
        'keywords': [
            'government scheme', 'govt scheme', 'schemes available', 'subsidy', 'financial aid', 'farmer benefits',
            'national horticulture mission', 'nhm', 'mission for integrated development of horticulture', 'midh',
            'arecanut garden rejuvenation scheme', 'rejuvenation scheme',
            'pradhan mantri fasal bima yojana', 'pmfby', 'crop insurance',
            'soil health card scheme', 'soil testing',
            'state-specific schemes', 'karnataka schemes', 'leaf spot disease assistance', 'leaf disease scheme',
            'icar cpcri', 'kvk demonstration', 'dasd mini mission projects', 'state-level plantation crop development',
            'meghalaya schemes', 'arecanut planting subsidy',
            'list schemes', 'all schemes', 'what schemes are there', 'tell me all schemes'
        ],
        'responses': [
            'There are several government schemes and support programs available for arecanut farmers in India. Could you please specify if you are looking for general information or details on a particular scheme like NHM, PMFBY, or a state-specific one?',
            'The government offers various initiatives to support arecanut cultivation, covering aspects from planting to disease management and insurance. What specific type of support are you interested in?'
        ],
        'schemes': {
            'national_horticulture_mission': {
                'name': 'National Horticulture Mission (NHM)',
                'type': 'Central Sector Scheme',
                'support': 'Subsidies for planting materials, drip irrigation, pest control, and post-harvest infrastructure.',
                'focus': 'Promotion of horticultural crops including arecanut.',
                'kannada': 'ರಾಷ್ಟ್ರೀಯ ತೋಟಗಾರಿಕೆ ಮಿಷನ್ (NHM) - ಸಸ್ಯ ಸಾಮಗ್ರಿಗಳು, ಹನಿ ನೀರಾವರಿ, ಕೀಟ ನಿಯಂತ್ರಣ ಮತ್ತು ಕೊಯ್ಲು ನಂತರದ ಮೂಲಸೌಕರ್ಯಗಳಿಗೆ ಸಹಾಯಧನ ನೀಡುತ್ತದೆ.'
            },
            'mission_integrated_development_horticulture': {
                'name': 'Mission for Integrated Development of Horticulture (MIDH)',
                'implemented_by': 'Directorate of Arecanut and Spices Development (DASD), Kozhikode',
                'support': 'Distribution of high-yielding planting materials; Frontline demonstrations for farmers; Farmer training and capacity building programs.',
                'kannada': 'ಸಂಯೋಜಿತ ತೋಟಗಾರಿಕೆ ಅಭಿವೃದ್ಧಿ ಮಿಷನ್ (MIDH) - ಹೆಚ್ಚಿನ ಇಳುವರಿ ನೀಡುವ ಸಸ್ಯ ಸಾಮಗ್ರಿಗಳ ವಿತರಣೆ, ರೈತರಿಗೆ ಪ್ರಾತ್ಯಕ್ಷಿಕೆಗಳು ಮತ್ತು ತರಬೇತಿ ಕಾರ್ಯಕ್ರಮಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ.'
            },
            'arecanut_garden_rejuvenation_scheme': {
                'name': 'Arecanut Garden Rejuvenation Scheme',
                'objective': 'Replacing senile or unproductive arecanut palms.',
                'support': '50% subsidy on seedlings (e.g., Calicut-17, Sumangala); Full transport cost covered for replanting; Financial aid for intercropping in rejuvenated gardens.',
                'kannada': 'ಅಡಿಕೆ ತೋಟ ಪುನಶ್ಚೇತನ ಯೋಜನೆ - ಅಡಿಕೆ ಗಿಡಗಳನ್ನು ಬದಲಾಯಿಸಲು 50% ಸಬ್ಸಿಡಿ, ಸಾಗಾಣಿಕೆ ವೆಚ್ಚ ಮತ್ತು ಅಂತರಬೆಳೆಗಳಿಗೆ ಆರ್ಥಿಕ ಸಹಾಯವನ್ನು ಒದಗಿಸುತ್ತದೆ.'
            },
            'pradhan_mantri_fasal_bima_yojana': {
                'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                'coverage': 'Crop insurance for horticultural crops (available in select regions).',
                'benefit': 'Compensation for crop loss due to natural calamities, pests, or diseases.',
                'kannada': 'ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY) - ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು, ಕೀಟಗಳು ಅಥವಾ ರೋಗಗಳಿಂದ ಬೆಳೆ ನಷ್ಟಕ್ಕೆ ಪರಿಹಾರವನ್ನು ಒದಗಿಸುವ ಬೆಳೆ ವಿಮೆ.'
            },
            'soil_health_card_scheme': {
                'name': 'Soil Health Card Scheme',
                'objective': 'Improve soil fertility.',
                'benefit': 'Customized fertilizer and micronutrient recommendations for arecanut plantations; Regular soil testing every 2 years.',
                'kannada': 'ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಯೋಜನೆ - ಅಡಿಕೆ ತೋಟಗಳಿಗೆ ಸೂಕ್ತ ರಸಗೊಬ್ಬರ ಮತ್ತು ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಶಿಫಾರಸುಗಳನ್ನು ನೀಡುತ್ತದೆ ಮತ್ತು ಪ್ರತಿ 2 ವರ್ಷಗಳಿಗೊಮ್ಮೆ ಮಣ್ಣು ಪರೀಕ್ಷೆಯನ್ನು ಖಚಿತಪಡಿಸುತ್ತದೆ.'
            },
            'leaf_spot_disease_assistance': { # State-Specific (Karnataka Focus)
                'name': 'Leaf Spot Disease Assistance (Karnataka - 2023-24)',
                'region': 'Coastal and Malnad districts of Karnataka',
                'support': '₹4 crore budget; ₹4,000/acre provided to small/marginal farmers for leaf spot control (fungicides, sprays).',
                'kannada': 'ಎಲೆಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಸಹಾಯ (ಕರ್ನಾಟಕ) - ಕರಾವಳಿ ಮತ್ತು ಮಲೆನಾಡು ಜಿಲ್ಲೆಗಳಲ್ಲಿ ಸಣ್ಣ/ಅತಿ ಸಣ್ಣ ರೈತರಿಗೆ ಪ್ರತಿ ಎಕರೆಗೆ ₹4,000 ಸಹಾಯಧನ ನೀಡಲಾಗುತ್ತದೆ.'
            },
            'subsidies_karnataka_horticulture': {
                'name': 'Subsidies from Karnataka Department of Horticulture',
                'support': 'Planting materials, irrigation equipment, vermicompost pits, etc.',
                'kannada': 'ಕರ್ನಾಟಕ ತೋಟಗಾರಿಕೆ ಇಲಾಖೆಯಿಂದ ಸಬ್ಸಿಡಿಗಳು - ಸಸ್ಯ ಸಾಮಗ್ರಿಗಳು, ನೀರಾವರಿ ಉಪಕರಣಗಳು, ಎರೆಹುಳು ಗೊಬ್ಬರ ಗುಂಡಿಗಳಿಗೆ ಸಹಾಯಧನ.'
            },
            'icar_cpcri_kvk_programs': {
                'name': 'ICAR – CPCRI / KVK Demonstration Programs',
                'support': 'Integrated cropping system demo (Arecanut + Black Pepper + Cocoa + Banana); Disease management training; High-yielding and disease-resistant variety promotion.',
                'kannada': 'ICAR – CPCRI / KVK ಪ್ರಾತ್ಯಕ್ಷಿಕೆ ಕಾರ್ಯಕ್ರಮಗಳು - ಸಂಯೋಜಿತ ಬೆಳೆ ಪದ್ಧತಿ, ರೋಗ ನಿರ್ವಹಣೆ ತರಬೇತಿ ಮತ್ತು ಹೆಚ್ಚಿನ ಇಳುವರಿ ನೀಡುವ ತಳಿಗಳ ಪ್ರಚಾರವನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ.'
            },
            'dasd_mini_mission_projects': {
                'name': 'DASD Mini Mission Projects',
                'region': 'Kerala, Karnataka, Goa, Maharashtra, NE states',
                'support': 'Small-scale demonstrations, capacity-building for farmers; Technology transfer and best practices for arecanut.',
                'kannada': 'DASD ಮಿನಿ ಮಿಷನ್ ಯೋಜನೆಗಳು - ಸಣ್ಣ ಪ್ರಮಾಣದ ಪ್ರಾತ್ಯಕ್ಷಿಕೆಗಳು, ರೈತರ ಸಾಮರ್ಥ್ಯ ನಿರ್ಮಾಣ ಮತ್ತು ತಂತ್ರಜ್ಞಾನ ವರ್ಗಾವಣೆಯನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ.'
            },
            'state_level_plantation_crop_development': {
                'name': 'State-Level Plantation Crop Development (e.g., Meghalaya)',
                'support': '50% subsidy for arecanut planting materials; Support for soakage tanks, fencing, and shade trees.',
                'kannada': 'ರಾಜ್ಯ ಮಟ್ಟದ ತೋಟಗಾರಿಕಾ ಬೆಳೆ ಅಭಿವೃದ್ಧಿ (ಉದಾ: ಮೇಘಾಲಯ) - ಅಡಿಕೆ ಸಸಿಗಳಿಗೆ 50% ಸಬ್ಸಿಡಿ, ನೀರು ಸಂಗ್ರಹ ತೊಟ್ಟಿಗಳು, ಬೇಲಿ ಮತ್ತು ನೆರಳು ಮರಗಳಿಗೆ ಬೆಂಬಲ.'
            }
        }
    }
}

# --- 2. Advanced Fuzzy Logic System (No changes needed here) ---
class AdvancedFuzzyLogicSystem:
    @staticmethod
    def get_disease_protocol(disease_name, confidence_score):
        protocols = {
            'bud_rot': {
                'urgency': 'HIGH - Immediate action required to save the tree.',
                'fungicides': ['1% Bordeaux mixture', 'Copper oxychloride 0.2%'],
                'culturalPractices': ['Remove and destroy infected tissues', 'Improve drainage', 'Avoid mechanical injuries'],
                'preventive': ['Prophylactic spraying before monsoon', 'Maintain garden hygiene'],
                'dosage': 'Spray 100-250 ml solution per palm, covering the crown.',
                'timing': 'Pre-monsoon and post-monsoon, or immediately upon symptom appearance.',
                'nutrition': 'Ensure balanced nutrition to strengthen tree immunity.',
                'postHarvest': 'No direct post-harvest protocol.'
            },
            'stem_bleeding': {
                'urgency': 'HIGH - Can be fatal if not treated promptly.',
                'fungicides': ['1% Bordeaux mixture (paint)', 'Propiconazole 0.1%'],
                'culturalPractices': ['Scrape off rotten tissue', 'Apply fungicide paste', 'Improve drainage around base'],
                'preventive': ['Avoid injuries during cultivation', 'Proper nutrition'],
                'dosage': 'Apply paste to scraped areas; drench base with solution.',
                'timing': 'Upon first observation of symptoms.',
                'nutrition': 'Ensure adequate Potassium (K) to improve stem strength.',
                'postHarvest': 'No direct post-harvest protocol.'
            },
            'mahali_koleroga': {
                'urgency': 'MEDIUM to HIGH - Can cause significant yield loss.',
                'fungicides': ['1% Bordeaux mixture', 'Copper oxychloride 0.2%'],
                'culturalPractices': ['Remove fallen nuts', 'Prune overcrowded leaves'],
                'preventive': ['Prophylactic spraying before monsoon', 'Ensure good air circulation'],
                'dosage': 'Spray entire bunches and surrounding leaves.',
                'timing': 'Onset of monsoon, repeat after 45 days if rain persists.',
                'nutrition': 'Balanced NPK to support fruit development.',
                'postHarvest': 'No direct post-harvest protocol.'
            },
            'root_rot': {
                'urgency': 'HIGH - Often leads to tree death.',
                'fungicides': ['Copper oxychloride (soil drench)', 'Trichoderma viride (bio-fungicide)'],
                'culturalPractices': ['Remove infected roots', 'Improve soil aeration', 'Avoid over-irrigation'],
                'preventive': ['Sterilize planting pits', 'Use healthy seedlings'],
                'dosage': 'Drench soil around affected palms (2-5 litres per palm).',
                'timing': 'Upon diagnosis, repeat as necessary.',
                'nutrition': 'Focus on root-strengthening nutrients like Phosphorus.',
                'postHarvest': 'Sanitize tools after working on affected plants.'
            },
            'bud_borer': {
                'urgency': 'MEDIUM - Can lead to secondary infections like bud rot.',
                'fungicides': ['(Not a fungicide, but insecticide)', 'Carbofuran 3G granules'],
                'culturalPractices': ['Remove damaged parts', 'Maintain garden hygiene'],
                'preventive': ['Regular monitoring of tender leaves'],
                'dosage': 'Apply granules in the leaf axils of affected palms.',
                'timing': 'Upon first appearance of damage.',
                'nutrition': 'General plant vigor helps resist pests.',
                'postHarvest': 'No direct post-harvest protocol.'
            },
            'yellow_leaf_disease': {
                'urgency': 'HIGH - Lethal, management focuses on spread prevention.',
                'fungicides': ['No chemical cure - vector control is key'],
                'culturalPractices': ['Remove and destroy infected palms (quarantine)', 'Control insect vectors'],
                'preventive': ['Plant resistant varieties (if available)', 'Regular inspection for early symptoms'],
                'dosage': 'N/A',
                'timing': 'N/A',
                'nutrition': 'Supportive nutrition for healthy growth, but won\'t cure.',
                'postHarvest': 'N/A'
            },
            'stem_cracking': {
                'urgency': 'MEDIUM - Indicates underlying stress.',
                'fungicides': ['None directly, manage underlying cause.'],
                'culturalPractices': ['Ensure consistent irrigation', 'Balance fertilizer application'],
                'preventive': ['Avoid extreme moisture fluctuations', 'Proper nutrient management'],
                'dosage': 'N/A',
                'timing': 'N/A',
                'nutrition': 'Review K and Ca levels; ensure micronutrient availability.',
                'postHarvest': 'N/A'
            },
            'anabe_roga': {
                'urgency': 'HIGH - Causes significant yield loss.',
                'fungicides': ['Fosetyl-Al (Aliette) 0.3%', 'Propiconazole'],
                'culturalPractices': ['Remove infected inflorescences and nuts', 'Maintain good air circulation'],
                'preventive': ['Prophylactic spraying during flowering stage'],
                'dosage': 'Spray inflorescence and young nuts thoroughly.',
                'timing': 'Onset of flowering and early fruit set.',
                'nutrition': 'Ensure adequate Boron for flower and fruit development.',
                'postHarvest': 'No direct post-harvest protocol.'
            },
            'fruit_rot': {
                'urgency': 'MEDIUM - Primarily post-harvest issue.',
                'fungicides': ['(Post-harvest dips) Sodium hypochlorite solution 1%', 'Propiconazole (pre-harvest)'],
                'culturalPractices': ['Harvest at correct maturity', 'Handle fruits carefully', 'Store in ventilated areas'],
                'preventive': ['Good orchard hygiene', 'Pre-harvest fungicide sprays if history of disease'],
                'dosage': 'Dip fruits for 5-10 minutes (post-harvest); spray pre-harvest.',
                'timing': 'Pre-harvest for prevention; post-harvest for treatment.',
                'nutrition': 'General good nutrition for fruit health.',
                'postHarvest': 'Proper drying and storage are critical.'
            }
        }
        return protocols.get(disease_name, {
            'urgency': 'LOW - Information not specific enough.',
            'fungicides': ['No specific recommendation without more details.'],
            'culturalPractices': ['Observe closely and consult local experts.'],
            'preventive': ['Maintain general tree health.'],
            'dosage': 'N/A',
            'timing': 'N/A',
            'nutrition': 'Balanced nutrition.',
            'postHarvest': 'N/A'
        })

    @staticmethod
    def recommend_pesticide(weather_data, pest_type, tree_age):
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 70)
        rainfall = weather_data.get('rainfall', 0)
        wind_speed = weather_data.get('windSpeed', 5)

        sprayability = 1.0

        if temp < 20 or temp > 35: sprayability *= 0.7
        elif 15 <= temp < 20 or 35 < temp <= 40: sprayability *= 0.85
        
        if humidity < 40 or humidity > 85: sprayability *= 0.75
        elif 80 < humidity <= 85: sprayability *= 0.9
        
        if rainfall > 10: sprayability *= 0.3
        elif 5 <= rainfall <= 10: sprayability *= 0.6
        
        if wind_speed > 15: sprayability *= 0.5
        elif 10 <= wind_speed <= 15: sprayability *= 0.8

        dosage_multiplier = 1.0
        if sprayability < 0.6: dosage_multiplier = 0.8
        elif sprayability > 0.85: dosage_multiplier = 1.1

        timing = "Optimal: Early morning or late afternoon."
        if rainfall > 0: timing = "Avoid spraying if rain is imminent or occurring."
        if wind_speed > 10: timing = "Consider spraying when wind calms."

        return {
            'sprayability': sprayability,
            'dosageMultiplier': dosage_multiplier,
            'timing': timing,
            'recommendedPesticide': 'General broad-spectrum for common pests'
        }

    @staticmethod
    def recommend_fertilizer(weather_data, soil_data, growth_stage, season):
        temp = weather_data.get('temperature', 28)
        rainfall = weather_data.get('rainfall', 50)
        pH = soil_data.get('pH', 6.5)
        organic_matter = soil_data.get('organicMatter', 3.0)

        base_n = 100
        base_p = 40
        base_k = 140

        if growth_stage == 'seedling' or growth_stage == 'juvenile':
            base_n *= 0.5
            base_p *= 0.5
            base_k *= 0.5
        elif growth_stage == 'flowering':
            base_p *= 1.2
            base_k *= 1.1
        elif growth_stage == 'fruiting':
            base_k *= 1.3
            base_n *= 1.1

        if pH < 6.0: 
            base_p *= 0.8
            base_k *= 0.9
        elif pH > 7.5:
            base_n *= 0.9
            base_p *= 0.9

        if organic_matter < 2.0:
            base_n *= 1.1
            base_p *= 1.1
            base_k *= 1.1
        elif organic_matter > 5.0:
            base_n *= 0.9

        application_rate = 1.0
        timing = "Apply in 2 split doses: Post-monsoon (Sep-Oct) and Pre-summer (Feb)."

        if rainfall > 100:
            application_rate *= 0.8
            timing = "Consider smaller, more frequent applications due to high rainfall."
        elif rainfall < 10:
            timing = "Ensure immediate irrigation after application to dissolve fertilizers."
            
        if temp < 20 or temp > 35:
            application_rate *= 0.9

        return {
            'npkRatio': {
                'nitrogen': round(base_n, 1),
                'phosphorus': round(base_p, 1),
                'potassium': round(base_k, 1)
            },
            'applicationRate': application_rate,
            'timing': timing
        }

    @staticmethod
    def predict_harvest_timing(conditions, historical_data, tree_age):
        maturity = conditions.get('fruitMaturity', 70)
        temp = conditions.get('temperature', 28)
        rainfall = conditions.get('rainfall', 50)
        humidity = conditions.get('humidity', 80)
        
        estimated_days_base = (100 - maturity) * 1.5

        quality_factor = 1.0

        if temp < 20 or temp > 35: estimated_days_base *= 1.1
        if rainfall > 100: estimated_days_base *= 0.9
        if humidity < 60: quality_factor *= 0.9

        if tree_age > 15:
            estimated_days_base *= 0.95
            quality_factor *= 1.05

        recommendation = "Monitor fruit color (turning yellow/orange) and firmness. Harvest in batches."
        market_timing = "Consider market demand for tender vs. ripe nuts."

        if maturity >= 90:
            estimated_days_base = max(0, estimated_days_base - 10)
            recommendation = "Initiate harvest! Fruits are nearing optimal maturity."
            quality_factor *= 1.1
        elif maturity < 60:
            recommendation = "Nuts are still immature. Continue monitoring."
            estimated_days_base = (100 - maturity) * 2.0

        return {
            'estimatedDays': math.ceil(estimated_days_base),
            'confidence': 'HIGH' if maturity >= 80 else 'MEDIUM',
            'qualityFactor': round(quality_factor, 2),
            'recommendation': recommendation,
            'marketTiming': market_timing
        }


# --- 3. Arecanut Chatbot Class (with debug prints and scheme handling) ---
class ArecanutChatbot:
    def __init__(self):
        self.knowledge_base = enhanced_knowledge_base
        self.threshold = 70
        self.specific_action_threshold = 85 

        self.current_intent = None
        self.collected_data = {}
        self.required_parameters = {}

        self.param_parsers = {
            'temperature': self._parse_single_param(r'(?:temp|temperature)\D*(\d+)', int),
            'humidity': self._parse_single_param(r'(?:humid|humidity)\D*(\d+)', int),
            'rainfall': self._parse_single_param(r'(?:rain|rainfall)\D*(\d+)', int),
            'windSpeed': self._parse_single_param(r'(?:wind|wind\s*speed)\D*(\d+)', int),
            'pH': self._parse_single_param(r'(?:ph|p\s*h)\D*(\d+\.?\d*)', float),
            'organicMatter': self._parse_single_param(r'(?:organic\s*matter|om)\D*(\d+\.?\d*)', float),
            'fruitMaturity': self._parse_single_param(r'(?:fruit\s*maturity|maturity)\D*(\d+)%?', int),
            'treeAge': self._parse_single_param(r'(?:tree\s*age|age)\D*(\d+)\s*(?:years?)?', int)
        }
        print("DEBUG: Chatbot initialized. Knowledge base keys:", self.knowledge_base.keys())

    def _fuzzy_match(self, user_input, keywords_list):
        max_score = 0
        for keyword in keywords_list:
            score = fuzz.ratio(user_input.lower(), keyword.lower())
            if score > max_score:
                max_score = score
        return max_score

    def _partial_fuzzy_match(self, user_input, keywords_list):
        max_score = 0
        for keyword in keywords_list:
            score = fuzz.partial_ratio(user_input.lower(), keyword.lower())
            if score > max_score:
                max_score = score
        return max_score
    
    def _parse_single_param(self, regex_pattern, data_type):
        def parser(message):
            match = re.search(regex_pattern, message, re.IGNORECASE)
            if match:
                try:
                    return data_type(match.group(1))
                except ValueError:
                    return None 
            return None
        return parser

    def _extract_all_parameters(self, message):
        extracted_params = {}
        for param_name, parser_func in self.param_parsers.items():
            value = parser_func(message)
            if value is not None:
                extracted_params[param_name] = value
        
        user_input_lower = message.lower()
        if 'seedling' in user_input_lower: extracted_params['growthStage'] = 'seedling'
        elif 'juvenile' in user_input_lower: extracted_params['growthStage'] = 'juvenile'
        elif 'flowering' in user_input_lower: extracted_params['growthStage'] = 'flowering'
        elif 'fruiting' in user_input_lower: extracted_params['growthStage'] = 'fruiting'
        elif 'mature' in user_input_lower: extracted_params['growthStage'] = 'mature' 

        if 'pre-monsoon' in user_input_lower or 'before rain' in user_input_lower: extracted_params['season'] = 'pre_monsoon'
        elif 'post-monsoon' in user_input_lower or 'after rain' in user_input_lower: extracted_params['season'] = 'post_monsoon'
        elif 'winter' in user_input_lower: extracted_params['season'] = 'winter'
        elif 'summer' in user_input_lower: extracted_params['season'] = 'summer'
        
        return extracted_params

    def _reset_context(self):
        print("DEBUG: Resetting context.")
        self.current_intent = None
        self.collected_data = {}
        self.required_parameters = {}

    def _get_missing_params_prompt(self, missing_params):
        prompts = {
            'temperature': 'temperature',
            'humidity': 'humidity',
            'rainfall': 'rainfall',
            'windSpeed': 'wind speed',
            'pH': 'soil pH',
            'organicMatter': 'organic matter percentage',
            'fruitMaturity': 'fruit maturity percentage',
            'treeAge': 'tree age in years'
        }
        
        if not missing_params:
            return ""

        missing_names = [prompts.get(p, p) for p in missing_params]
        if len(missing_names) == 1:
            return f"I need the {missing_names[0]}."
        elif len(missing_names) == 2:
            return f"I need the {missing_names[0]} and {missing_names[1]}."
        else:
            return f"I need the {', '.join(missing_names[:-1])}, and {missing_names[-1]}."

    def get_bot_response(self, user_message):
        user_input_lower = user_message.lower().strip() # Strip whitespace

        # --- NEW: Handle empty or very short/unclear inputs ---
        if not user_input_lower:
            return "Please type your query. I'm ready to assist you with arecanut farming!"
        
        # Heuristic for very short or non-meaningful inputs
        # Check if the input is mostly punctuation or numbers, or just a very short string
        if len(user_input_lower) < 3 and not re.search(r'[a-zA-Z]{2,}', user_input_lower):
            # Example: "k", ".", "1", "??", etc.
            self._reset_context()
            return "I'm sorry, I couldn't understand that. Could you please type a more complete query?"
        # --- END NEW ---

        print(f"\nDEBUG: User Input: '{user_input_lower}'")

        # 1. Handle greetings and thanks first (high confidence direct match)
        for category in ['greeting', 'thanks']:
            for keyword in self.knowledge_base[category]['keywords']:
                if fuzz.ratio(user_input_lower, keyword.lower()) >= 90: 
                    self._reset_context() 
                    print(f"DEBUG: Matched to {category} with high confidence.")
                    return random.choice(self.knowledge_base[category]['responses'])

        # 2. If an intent is currently active, try to collect parameters for it
        if self.current_intent:
            print(f"DEBUG: Current active intent: {self.current_intent}. Attempting to collect parameters.")
            extracted_params = self._extract_all_parameters(user_input_lower)
            self.collected_data.update(extracted_params) 
            print(f"DEBUG: Collected data so far: {self.collected_data}")

            if self.current_intent == 'fertilizer':
                if 'growthStage' not in self.collected_data: 
                    if 'seedling' in user_input_lower: self.collected_data['growthStage'] = 'seedling'
                    elif 'juvenile' in user_input_lower: self.collected_data['growthStage'] = 'juvenile'
                    elif 'flowering' in user_input_lower: self.collected_data['growthStage'] = 'flowering'
                    elif 'fruiting' in user_input_lower: self.collected_data['growthStage'] = 'fruiting'
                    elif 'mature' in user_input_lower: self.collected_data['growthStage'] = 'mature'
                
                if 'season' not in self.collected_data: 
                    if 'pre-monsoon' in user_input_lower or 'before rain' in user_input_lower: self.collected_data['season'] = 'pre_monsoon'
                    elif 'post-monsoon' in user_input_lower or 'after rain' in user_input_lower: self.collected_data['season'] = 'post_monsoon'
                    elif 'winter' in user_input_lower: self.collected_data['season'] = 'winter'
                    elif 'summer' in user_input_lower: self.collected_data['season'] = 'summer'

            missing_params = [
                p for p in self.required_parameters
                if p not in self.collected_data or self.collected_data[p] is None
            ]
            print(f"DEBUG: Missing parameters for current intent: {missing_params}")

            if not missing_params: 
                print(f"DEBUG: All parameters collected for {self.current_intent}.")
                response = self._generate_detailed_response(self.current_intent)
                self._reset_context() 
                return response
            else:
                return f"Okay, I've got that. {self._get_missing_params_prompt(missing_params)} Can you provide it?"

        # 3. If no active intent, or previous intent completed, classify a new intent
        best_match_category = 'unrecognized'
        max_score = 0
        is_list_schemes_query = False 

        for category_name, data in self.knowledge_base.items():
            if category_name in ['greeting', 'thanks', 'unrecognized']:
                continue

            current_category_score = self._partial_fuzzy_match(user_input_lower, data.get('keywords', []))
            print(f"DEBUG: Checking category '{category_name}'. Score: {current_category_score}")
            
            # Special handling for disease category: prioritize exact disease name matches
            if category_name == 'disease' and 'diseases' in data:
                found_disease_key = None
                for disease_key in data['diseases'].keys():
                    disease_name_variations = [
                        disease_key.replace('_', ' '),
                        disease_key.replace('_', ''),
                        disease_key.split('_')[0] if '_' in disease_key else disease_key
                    ]
                    for variation in disease_name_variations:
                        if fuzz.partial_ratio(user_input_lower, variation) >= self.specific_action_threshold:
                            found_disease_key = disease_key
                            break
                    if found_disease_key:
                        break

                if found_disease_key:
                    self._reset_context() 
                    print(f"DEBUG: Matched specific disease: {found_disease_key}.")
                    return self._generate_detailed_response('disease', specific_disease=found_disease_key)

            # Special handling for government_schemes: prioritize specific scheme names AND "list all" queries
            if category_name == 'government_schemes' and 'schemes' in data:
                # Check for explicit "list all schemes" type queries
                list_keywords = ['list schemes', 'all schemes', 'what schemes are there', 'tell me all schemes']
                for kw in list_keywords:
                    if fuzz.partial_ratio(user_input_lower, kw) >= 85: # High threshold for this specific command
                        is_list_schemes_query = True
                        break
                
                if is_list_schemes_query:
                    self._reset_context()
                    print(f"DEBUG: Matched 'list all schemes' query.")
                    return self._generate_detailed_response('government_schemes', list_all=True)


                # Check for specific scheme name matches (if not a "list all" query)
                found_scheme_key = None
                for scheme_key in data['schemes'].keys():
                    scheme_name_variations = [
                        scheme_key.replace('_', ' ').lower(),
                        data['schemes'][scheme_key]['name'].lower(),
                        scheme_key.split('_')[0] if '_' in scheme_key else scheme_key
                    ]
                    if 'nhm' in scheme_key: scheme_name_variations.append('nhm')
                    if 'midh' in scheme_key: scheme_name_variations.append('midh')
                    if 'pmfby' in scheme_key: scheme_name_variations.append('pmfby')
                    if 'cpcri' in scheme_key: scheme_name_variations.append('cpcri')
                    if 'kvk' in scheme_key: scheme_name_variations.append('kvk')
                    if 'dasd' in scheme_key: scheme_name_variations.append('dasd')

                    for variation in scheme_name_variations:
                        if fuzz.partial_ratio(user_input_lower, variation) >= self.specific_action_threshold:
                            found_scheme_key = scheme_key
                            break
                    if found_scheme_key:
                        break

                if found_scheme_key:
                    self._reset_context() 
                    print(f"DEBUG: Matched specific scheme: {found_scheme_key}.")
                    return self._generate_detailed_response('government_schemes', specific_scheme=found_scheme_key)
            
            # Update best match if current category score is higher
            if current_category_score > max_score:
                max_score = current_category_score
                best_match_category = category_name
        
        print(f"DEBUG: Best overall match found: '{best_match_category}' with score {max_score}. Threshold: {self.threshold}")

        if max_score < self.threshold:
            self._reset_context() 
            print(f"DEBUG: No category reached threshold {self.threshold}.")
            return "I'm sorry, I don't understand your query. Please ask me about arecanut farming, diseases, fertilizers, pesticides, harvest, or government schemes."

        # Set the new current intent and extract parameters from the initial message
        self.current_intent = best_match_category
        self.collected_data = self._extract_all_parameters(user_input_lower)
        self.required_parameters = self.knowledge_base[best_match_category].get('required_params', [])
        
        print(f"DEBUG: New intent set: {self.current_intent}. Required params: {self.required_parameters}. Collected data: {self.collected_data}")

        missing_params = [
            p for p in self.required_parameters
            if p not in self.collected_data or self.collected_data[p] is None
        ]

        if not missing_params: 
            print(f"DEBUG: All parameters provided in first turn for {self.current_intent}.")
            response = self._generate_detailed_response(self.current_intent)
            self._reset_context() 
            return response
        else:
            if self.required_parameters:
                print(f"DEBUG: Asking for missing parameters for {self.current_intent}.")
                return f"{random.choice(self.knowledge_base[best_match_category]['responses'])} {self._get_missing_params_prompt(missing_params)}"
            else: 
                print(f"DEBUG: Providing general response for {self.current_intent}.")
                self._reset_context()
                return random.choice(self.knowledge_base[best_match_category]['responses'])

    # --- Response Generation for Specific Intents ---
    def _generate_detailed_response(self, intent_name, specific_disease=None, specific_scheme=None, list_all=False):
        print(f"DEBUG: In _generate_detailed_response for intent: {intent_name}, specific_disease: {specific_disease}, specific_scheme: {specific_scheme}, list_all: {list_all}")
        
        if intent_name == 'disease':
            if specific_disease:
                protocol = AdvancedFuzzyLogicSystem.get_disease_protocol(specific_disease, 50)
                disease_info = self.knowledge_base['disease']['diseases'][specific_disease]
                response_text = f"🦠 **{specific_disease.replace('_', ' ').upper()} - COMPREHENSIVE TREATMENT PROTOCOL**\n\n"
                response_text += f"📋 **Disease Description:**\n{disease_info}\n\n"
                response_text += f"🚨 **Urgency Level:** {protocol['urgency']}\n\n"
                if protocol.get('fungicides'):
                    response_text += "💊 **Recommended Fungicides:**\n" + '\n'.join([f"• {f}" for f in protocol['fungicides']]) + "\n\n"
                if protocol.get('culturalPractices'):
                    response_text += "🌿 **Cultural Practices:**\n" + '\n'.join([f"• {p}" for p in protocol['culturalPractices']]) + "\n\n"
                if protocol.get('preventive'):
                    response_text += "🛡️ **Preventive Measures:**\n" + '\n'.join([f"• {p}" for p in protocol['preventive']]) + "\n\n"
                response_text += "⚠️ **Application Instructions:**\n"
                response_text += f"• {protocol.get('dosage', 'Follow label recommendations')}\n"
                response_text += f"• {protocol.get('timing', 'Apply during favorable weather')}\n"
                if protocol.get('nutrition'):
                    response_text += f"• Nutrition: {protocol['nutrition']}\n"
                if protocol.get('postHarvest'):
                    response_text += f"• Post-harvest: {protocol['postHarvest']}\n"
                response_text += "\n💡 **Additional Notes:**\nFor precise weather-based application timing, provide current weather data (temperature, humidity, rainfall, wind speed)."
                return response_text
            else:
                return random.choice(self.knowledge_base['disease']['responses']) 
        
        elif intent_name == 'pesticide':
            weather_data = {k: self.collected_data.get(k) for k in ['temperature', 'humidity', 'rainfall', 'windSpeed']}
            recommendation = AdvancedFuzzyLogicSystem.recommend_pesticide(weather_data, 'general', self.collected_data.get('treeAge', 10)) 
            spray_status = ''; status_icon = ''
            if recommendation['sprayability'] > 0.7: spray_status = 'EXCELLENT'; status_icon = '✅'
            elif recommendation['sprayability'] > 0.4: spray_status = 'MODERATE'; status_icon = '⚠️'
            else: spray_status = 'POOR'; status_icon = '❌'
            response_text = f"🌦️ **WEATHER-BASED PESTICIDE RECOMMENDATION**\n\n" \
                            f"{status_icon} **Spray Conditions: {spray_status}**\n\n" \
                            f"📊 **Detailed Weather Analysis:**\n" \
                            f"• 🌡️ Temperature: {weather_data['temperature']}°C {'✅ Optimal' if 20 <= weather_data['temperature'] <= 35 else '⚠️ Suboptimal'}\n" \
                            f"• 💧 Humidity: {weather_data['humidity']}% {'✅ Good' if 40 <= weather_data['humidity'] <= 80 else '⚠️ Challenging'}\n" \
                            f"• 🌧️ Rainfall: {weather_data['rainfall']}mm {'✅ Safe' if weather_data['rainfall'] < 5 else '❌ Wait'}\n" \
                            f"• 💨 Wind Speed: {weather_data['windSpeed']}kmph {'✅ Suitable' if weather_data['windSpeed'] < 15 else '⚠️ Risky'}\n\n" \
                            f"💊 **Application Recommendations:**\n" \
                            f"• **Dosage Multiplier:** {recommendation['dosageMultiplier']:.2f}x standard rate\n" \
                            f"• **Sprayability Score:** {int(recommendation['sprayability'] * 100)}%\n" \
                            f"• **Optimal Timing:** {recommendation['timing']}\n\n" \
                            f"📋 **Action Plan:**\n"
            if recommendation['sprayability'] > 0.7: response_text += '• Proceed with spraying\n• Use recommended dosage\n• Monitor for effectiveness'
            elif recommendation['sprayability'] > 0.4: response_text += '• Spray with caution\n• Consider adjusting timing\n• Monitor weather changes'
            else: response_text += '• Postpone spraying\n• Wait for better conditions\n• Protect equipment from weather'
            response_text += "\n\n⚠️ **Safety Reminders:**\n• Wear protective equipment\n• Avoid spraying during peak sun hours\n• Ensure proper coverage without wastage"
            return response_text

        elif intent_name == 'fertilizer':
            weather_data = {k: self.collected_data.get(k) for k in ['temperature', 'humidity', 'rainfall']}
            soil_data = {k: self.collected_data.get(k) for k in ['pH', 'organicMatter']}
            growth_stage = self.collected_data.get('growthStage', 'mature')
            season = self.collected_data.get('season', 'post_monsoon')
            recommendation = AdvancedFuzzyLogicSystem.recommend_fertilizer(weather_data, soil_data, growth_stage, season)
            response_text = "🌱 **PRECISION FERTILIZER RECOMMENDATION SYSTEM**\n\n" \
                            f"📊 **Calculated NPK Requirements:**\n" \
                            f"• 🟢 **Nitrogen (N):** {recommendation['npkRatio']['nitrogen']}g per palm\n" \
                            f"• 🟡 **Phosphorus (P₂O₅):** {recommendation['npkRatio']['phosphorus']}g per palm\n" \
                            f"• 🔴 **Potassium (K₂O):** {recommendation['npkRatio']['potassium']}g per palm\n\n" \
                            f"💧 **Weather-Adjusted Application Rate:** {recommendation['applicationRate']:.2f}x base rate\n\n" \
                            f"🌡️ **Current Conditions Analysis:**\n" \
                            f"• Temperature: {weather_data['temperature']}°C - {'✅ Optimal uptake' if 20 <= weather_data['temperature'] <= 35 else '⚠️ Reduced efficiency'}\n" \
                            f"• Humidity: {weather_data['humidity']}% - Nutrient mobility: {'🔝 High' if weather_data['humidity'] >= 60 else '📉 Moderate'}\n" \
                            f"• Rainfall: {weather_data['rainfall']}mm - Leaching risk: {'🔴 High' if weather_data['rainfall'] > 50 else '🟢 Low'}\n\n" \
                            f"🎯 **Soil Condition Assessment:**\n" \
                            f"• pH Level: {soil_data['pH']} - {'✅ Ideal' if 6.0 <= soil_data['pH'] <= 7.5 else '⚠️ Needs adjustment'}\n" \
                            f"• Organic Matter: {soil_data['organicMatter']}% - {'✅ Good' if soil_data['organicMatter'] >= 2 else '⚠️ Low, consider amendments'}\n\n" \
                            f"📅 **Optimal Application Timing:** {recommendation['timing']}\n\n" \
                            f"💡 **Actionable Advice:**\n" \
                            "• Consider a soil test if NPK levels are estimates.\n" \
                            "• Split application for better nutrient absorption, especially in sandy soils.\n" \
                            "• Incorporate organic matter to improve soil health and nutrient retention."
            return response_text

        elif intent_name == 'harvest':
            current_conditions = {k: self.collected_data.get(k) for k in ['fruitMaturity', 'temperature', 'rainfall', 'humidity']}
            tree_age = self.collected_data.get('treeAge', 10)
            prediction = AdvancedFuzzyLogicSystem.predict_harvest_timing(current_conditions, {}, tree_age)
            response_text = f"📅 **ARECANUT HARVEST PREDICTION**\n\n" \
                            f"📈 **Estimated Days to Harvest:** **{prediction['estimatedDays']} days**\n" \
                            f"Confidence Level: **{prediction['confidence']}**\n\n" \
                            f"📊 **Current Conditions Impact:**\n" \
                            f"• Fruit Maturity: {current_conditions['fruitMaturity']}%\n" \
                            f"• Temperature: {current_conditions['temperature']}°C\n" \
                            f"• Rainfall: {current_conditions['rainfall']}mm\n" \
                            f"• Humidity: {current_conditions['humidity']}%\n\n" \
                            f"⭐ **Expected Quality Factor:** **{prediction['qualityFactor']}**\n\n" \
                            f"📋 **Harvesting Recommendations:**\n" \
                            f"• **Action Plan:** {prediction['recommendation']}\n" \
                            f"• **Market Advice:** {prediction['marketTiming']}\n\n" \
                            "💡 **Pro Tips:**\n" \
                            "• Monitor fruit color and firmness regularly.\n" \
                            "• Plan for labor and transportation well in advance.\n" \
                            "• Consider post-harvest processing options to maximize value."
            return response_text
        
        elif intent_name == 'government_schemes':
            if list_all:
                response_text = "🏛️ **AVAILABLE GOVERNMENT SCHEMES FOR ARECANUT FARMERS:**\n\n"
                for scheme_key, scheme_info in self.knowledge_base['government_schemes']['schemes'].items():
                    name = scheme_info.get('name', scheme_key.replace('_', ' ').title())
                    response_text += f"• {name}\n"
                response_text += "\nTo get more details about a specific scheme, please ask me its name (e.g., 'Tell me about the National Horticulture Mission')."
                return response_text
            elif specific_scheme:
                scheme_data = self.knowledge_base['government_schemes']['schemes'].get(specific_scheme)
                if scheme_data:
                    response_text = f"🏛️ **{scheme_data['name'].upper()}**\n\n"
                    if 'type' in scheme_data: response_text += f"**Type:** {scheme_data['type']}\n"
                    if 'implemented_by' in scheme_data: response_text += f"**Implemented by:** {scheme_data['implemented_by']}\n"
                    if 'objective' in scheme_data: response_text += f"**Objective:** {scheme_data['objective']}\n"
                    if 'coverage' in scheme_data: response_text += f"**Coverage:** {scheme_data['coverage']}\n"
                    if 'support' in scheme_data: response_text += f"**Support/Benefit:** {scheme_data['support']}\n"
                    if 'focus' in scheme_data: response_text += f"**Focus:** {scheme_data['focus']}\n"
                    if 'region' in scheme_data: response_text += f"**Region:** {scheme_data['region']}\n"
                    if 'benefit' in scheme_data: response_text += f"**Benefit:** {scheme_data['benefit']}\n"
                    
                    if 'kannada' in scheme_data:
                        response_text += f"\n**ಕನ್ನಡದಲ್ಲಿ:** {scheme_data['kannada']}"
                    return response_text
                else:
                    return f"I couldn't find specific details for '{specific_scheme.replace('_', ' ')}'. Please try a more general query about government schemes or ask me to list them."
            else:
                return random.choice(self.knowledge_base['government_schemes']['responses'])


        # All other static info categories
        elif intent_name in ['weather', 'general', 'arecanut_info', 'climate_soil', 'propagation', 'planting', 'irrigation', 'manuring', 'intercropping']:
            print(f"DEBUG: Handling static info intent: {intent_name}. Responses available: {len(self.knowledge_base[intent_name]['responses'])}")
            if self.knowledge_base[intent_name]['responses']:
                return random.choice(self.knowledge_base[intent_name]['responses'])
            else:
                print(f"ERROR: No responses found for intent: {intent_name}")
                return "I'm sorry, I have information on that, but no response is available. Please contact support."


        # Fallback if unrecognized or unhandled specific intent
        print(f"DEBUG: Fallback: No specific response generated for {intent_name} or conditions not met.")
        return "I'm sorry, I couldn't generate a specific response for that with the provided information. Can you try rephrasing or providing more details?"

# --- 4. Main Chat Loop (How to run the chatbot) ---
if __name__ == "__main__":
    bot = ArecanutChatbot()
    print("Welcome to Arecanut Chatbot! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye! Happy farming!")
            break
        
        response = bot.get_bot_response(user_input)
        print(f"Chatbot: {response}")