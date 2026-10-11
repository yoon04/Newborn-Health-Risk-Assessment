(function () {
  'use strict';

  if (window.NHRA_LANGUAGE !== 'my') return;

  const translations = {
    'Newborn Health Risk Assessment': 'မွေးကင်းစကလေး ကျန်းမာရေးအန္တရာယ် အကဲဖြတ်ခြင်း',
    'Risk Assessment Results': 'အန္တရာယ် အကဲဖြတ် ရလဒ်များ',
    'Assessment History · Newborn Health Risk Assessment': 'အကဲဖြတ် မှတ်တမ်း · မွေးကင်းစကလေး ကျန်းမာရေး',
    'My Profile': 'ကျွန်ုပ်၏ Profile',
    'Preferred language': 'နှစ်သက်ရာ ဘာသာစကား',
    'Main navigation': 'အဓိက လမ်းညွှန်',
    'Neonatal Assessment Dashboard': 'မွေးကင်းစကလေး ကျန်းမာရေး အကဲဖြတ်စနစ်',
    'New Assessment': 'အကဲဖြတ်မှုအသစ်',
    'Shared History': 'မှတ်တမ်းများ',
    'Newborn Health': 'မွေးကင်းစကလေး ကျန်းမာရေး',
    'Risk Assessment': 'အန္တရာယ် အကဲဖြတ်ခြင်း',
    'Assess newborn health indicators with a clear, summarized risk report.': 'မွေးကင်းစကလေး၏ ကျန်းမာရေးအချက်အလက်များကို ရှင်းလင်းသော အန္တရာယ်အစီရင်ခံစာဖြင့် အကဲဖြတ်ပါ။',
    'APGAR': 'APGAR',
    'Birth Info': 'မွေးဖွားမှု အချက်အလက်',
    'Family History': 'မိသားစု ကျန်းမာရေးရာဇဝင်',
    'Review': 'ပြန်လည်စစ်ဆေးရန်',
    'Important:': 'အရေးကြီးချက်:',
    'Educational use only. This does not replace professional medical advice.': 'ပညာပေးရန်သာ ဖြစ်ပြီး ကျန်းမာရေးပညာရှင်၏ အကြံဉာဏ်ကို အစားမထိုးပါ။',
    'APGAR observation record': 'APGAR စောင့်ကြည့်မှု မှတ်တမ်း',
    'Record the components observed at each minute. A total is derived only when all five score components are recorded.': 'အချိန်တစ်ခုစီတွင် တွေ့ရှိသည့် အချက်များကို မှတ်တမ်းတင်ပါ။ အမှတ်ပေးအချက်ငါးခုလုံး ပြည့်စုံမှသာ စုစုပေါင်းအမှတ်ကို တွက်ချက်ပါမည်။',
    'Component': 'အကဲဖြတ်ချက်',
    '1 minute': '၁ မိနစ်',
    '5 minutes': '၅ မိနစ်',
    'Appearance': 'အရေပြားအရောင်',
    'Skin colour': 'အရေပြားအရောင်',
    'Pulse': 'နှလုံးခုန်နှုန်း',
    'Heart rate': 'နှလုံးခုန်နှုန်း',
    'Reflex response': 'တုံ့ပြန်မှု',
    'Response to stimulation': 'လှုံ့ဆော်မှုအပေါ် တုံ့ပြန်မှု',
    'Muscle tone': 'ကြွက်သားတင်းအား',
    'Activity': 'လှုပ်ရှားမှု',
    'Respiration': 'အသက်ရှူခြင်း',
    'Breathing effort': 'အသက်ရှူအား',
    'Support/resuscitation': 'အသက်ကယ်အကူအညီ',
    'Documented support only; not included in the APGAR total.': 'မှတ်တမ်းတင်ရန်သာဖြစ်ပြီး APGAR စုစုပေါင်းအမှတ်တွင် မပါဝင်ပါ။',
    'Select score': 'အမှတ်ရွေးပါ',
    'Not recorded': 'မမှတ်တမ်းတင်ထားပါ',
    'Unknown / not recorded': 'မသိရှိ / မမှတ်တမ်းတင်ထားပါ',
    '0 — Blue/pale all over': '0 — ကိုယ်ခန္ဓာတစ်ခုလုံး ပြာ/ဖြူဖျော့',
    '1 — Pink body, blue extremities': '1 — ကိုယ်လုံးပန်းရောင်၊ လက်ခြေပြာ',
    '2 — Fully pink': '2 — ကိုယ်ခန္ဓာတစ်ခုလုံး ပန်းရောင်',
    '0 — Absent': '0 — မရှိ',
    '1 — Below 100 bpm': '1 — တစ်မိနစ်လျှင် ၁၀၀ bpm အောက်',
    '2 — 100+ bpm': '2 — တစ်မိနစ်လျှင် ၁၀၀ bpm နှင့်အထက်',
    '0 — No response': '0 — တုံ့ပြန်မှုမရှိ',
    '1 — Grimace only': '1 — မျက်နှာရှုံ့တုံ့ပြန်မှုသာ',
    '2 — Cry/cough/sneeze': '2 — ငို/ချောင်းဆိုး/နှာချေ',
    '0 — Limp': '0 — ပျော့ခွေ',
    '1 — Some flexion': '1 — အနည်းငယ်ကွေးနိုင်',
    '2 — Active movement': '2 — တက်ကြွစွာ လှုပ်ရှား',
    '1 — Weak/irregular': '1 — အားနည်း/မမှန်',
    '2 — Strong cry': '2 — အသံကျယ်စွာ ငို',
    'None': 'မရှိ',
    'Provided': 'ပေးထားသည်',
    '1-minute observation': '၁ မိနစ် စောင့်ကြည့်ချက်',
    '5-minute observation': '၅ မိနစ် စောင့်ကြည့်ချက်',
    '10-minute observation': '၁၀ မိနစ် စောင့်ကြည့်ချက်',
    'Not recorded or incomplete.': 'မမှတ်တမ်းတင်ထားပါ သို့မဟုတ် မပြည့်စုံပါ။',
    'Clinical warning': 'အရေးပေါ် သတိပေးချက်',
    'Heartbeat or breathing concern. Assess immediately.': 'နှလုံးခုန်ခြင်း သို့မဟုတ် အသက်ရှူခြင်း စိုးရိမ်ရသည်။ ချက်ချင်း စစ်ဆေးပါ။',
    'Blue/pale colour, absent reflex, or limp tone. Assess immediately.': 'ကိုယ်အရောင်ပြာ/ဖြူဖျော့ခြင်း၊ တုံ့ပြန်မှုမရှိခြင်း သို့မဟုတ် ပျော့ခွေခြင်းရှိသည်။ ချက်ချင်း စစ်ဆေးပါ။',
    'Reduced reflex or tone. Reassess clinically.': 'တုံ့ပြန်မှု သို့မဟုတ် ကြွက်သားတင်းအား လျော့နည်းသည်။ ဆေးဘက်ဆိုင်ရာ ပြန်လည်စစ်ဆေးပါ။',
    'Critical total. Assess immediately; do not delay care.': 'စုစုပေါင်းအမှတ် အရေးပေါ်အဆင့်ဖြစ်သည်။ ချက်ချင်း စစ်ဆေးပြီး ကုသမှု မနှောင့်နှေးပါနှင့်။',
    'APGAR below 7. Record the next 5-minute observation. Do not delay care.': 'APGAR ၇ အောက်ဖြစ်သည်။ နောက် ၅ မိနစ်အကြာ စောင့်ကြည့်ချက်ကို မှတ်တမ်းတင်ပါ။ ကုသမှု မနှောင့်နှေးပါနှင့်။',
    'Total is 7 or higher. Check component warnings.': 'စုစုပေါင်းအမှတ် ၇ သို့မဟုတ် အထက်ဖြစ်သည်။ အချက်တစ်ခုချင်း၏ သတိပေးချက်များကို စစ်ဆေးပါ။',
    'Birth Information': 'မွေးဖွားမှုနှင့်ဆိုင်သော အချက်အလက်များ',
    'Baby and birth identity': 'ကလေးနှင့် မွေးဖွားမှု အချက်အလက်',
    'Birth plurality': 'မွေးဖွားသည့် ကလေးအရေအတွက်',
    'Singleton — one baby': 'တစ်ဦးတည်း — ကလေးတစ်ဦး',
    'Twins — two babies': 'အမွှာ — ကလေးနှစ်ဦး',
    'Other multiple birth — three or more babies': 'အခြားအမြွှာမွေးဖွားမှု — ကလေးသုံးဦးနှင့်အထက်',
    'Which twin is this assessment for?': 'ဤအကဲဖြတ်ချက်သည် မည်သည့်အမွှာအတွက် ဖြစ်သနည်း။',
    "Baby's Name": 'ကလေးအမည်',
    'Twin 1 name': 'ပထမအမွှာ အမည်',
    'Twin 2 name': 'ဒုတိယအမွှာ အမည်',
    'Birth measurements': 'မွေးဖွားချိန် တိုင်းတာချက်များ',
    'Gestational Age (Weeks)': 'ကိုယ်ဝန်ဆောင်ချိန်ကာလ (ပတ်)',
    "Mother's Age (Years)": 'မိခင်အသက် (နှစ်)',
    "Mother's Age": 'မိခင်အသက်',
    "Child's Gender": 'ကလေး၏ လိင်',
    'Male': 'ကျား',
    'Female': 'မ',
    'Birth Weight': 'မွေးဖွားပြီးစ ကလေး၏ ကိုယ်အလေးချိန်',
    'Delivery details': 'မွေးဖွားမှု အသေးစိတ်',
    'Delivery Method': 'မွေးဖွားနည်း',
    'Vaginal Delivery': 'ရိုးရိုးမွေးဖွားခြင်း',
    'Assisted Delivery': 'အကူကိရိယာဖြင့် မွေးဖွားခြင်း',
    'Cesarean Section (C-Section)': 'ခွဲစိတ်မွေးဖွားခြင်း (C-Section)',
    'Delivery Complication': 'မွေးဖွားစဉ် နောက်ဆက်တွဲပြဿနာ',
    'No': 'မရှိ',
    'Yes': 'ရှိ',
    'Reported complication type': 'မှတ်တမ်းတင်ထားသော နောက်ဆက်တွဲပြဿနာအမျိုးအစား',
    'Select every complication that was reported. These details are documented for context; the current risk calculation uses only whether any complication was reported.': 'မှတ်တမ်းတင်ထားသော ပြဿနာအားလုံးကို ရွေးပါ။ အသေးစိတ်အချက်များသည် မှတ်တမ်းအတွက်ဖြစ်ပြီး လက်ရှိအန္တရာယ်တွက်ချက်မှုတွင် ပြဿနာရှိ/မရှိကိုသာ အသုံးပြုပါသည်။',
    'Fetal distress or non-reassuring fetal status': 'သန္ဓေသား အန္တရာယ်လက္ခဏာ သို့မဟုတ် စိတ်မချရသော အခြေအနေ',
    'Meconium-stained amniotic fluid': 'ကလေးအညစ်အကြေးပါသော ရေမြွှာရည်',
    'Umbilical cord complication': 'ချက်ကြိုးဆိုင်ရာ ပြဿနာ',
    'Prolonged or obstructed labor': 'မွေးဖွားချိန်ကြာမြင့်ခြင်း သို့မဟုတ် လမ်းပိတ်ခြင်း',
    'Premature or prolonged rupture of membranes': 'ရေမြွှာစောစီးစွာ သို့မဟုတ် ကြာမြင့်စွာ ပေါက်ခြင်း',
    'Maternal fever or suspected infection during labor': 'မွေးဖွားစဉ် မိခင်ဖျားခြင်း သို့မဟုတ် ကူးစက်ရောဂါ သံသယ',
    'Shoulder dystocia or difficult delivery': 'ပခုံးညပ်ခြင်း သို့မဟုတ် မွေးဖွားရခက်ခဲခြင်း',
    'Significant bleeding or placental complication': 'သွေးထွက်များခြင်း သို့မဟုတ် အချင်းဆိုင်ရာ ပြဿနာ',
    'Other reported delivery complication': 'အခြားမှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာ',
    'Complication reported, type unknown or not documented': 'ပြဿနာရှိကြောင်း မှတ်တမ်းတင်ထားသော်လည်း အမျိုးအစားမသိ/မဖော်ပြထားပါ',
    'Family Disease History': 'မိသားစု ရောဂါရာဇဝင်',
    'Is there a known family disease?': 'မိသားစုတွင် သိရှိထားသော ရောဂါရှိပါသလား။',
    'Unknown': 'မသိရှိပါ',
    'Reported family conditions': 'မှတ်တမ်းတင်ထားသော မိသားစုရောဂါများ',
    'Condition': 'ရောဂါအခြေအနေ',
    'Disease name': 'ရောဂါအမည်',
    'Who has this disease?': 'မည်သူတွင် ဤရောဂါရှိသနည်း။',
    'Father': 'ဖခင်',
    'Mother': 'မိခင်',
    'Both parents': 'မိဘနှစ်ဦးလုံး',
    'Other family member': 'အခြားမိသားစုဝင်',
    'Remove': 'ဖယ်ရှားရန်',
    'Add another disease': 'နောက်ထပ်ရောဂါ ထည့်ရန်',
    'Asthma': 'ပန်းနာရင်ကျပ်ရောဂါ',
    'Blood clotting disorder': 'သွေးခဲမှု မမှန်ခြင်း',
    'Breast cancer': 'ရင်သားကင်ဆာ',
    'Colorectal cancer': 'အူမကြီးနှင့် အစာဟောင်းအိမ် ကင်ဆာ',
    'Congenital heart disease': 'မွေးရာပါ နှလုံးရောဂါ',
    'Cystic fibrosis': 'Cystic fibrosis (မျိုးရိုးဗီဇရောဂါ)',
    'Diabetes': 'ဆီးချိုရောဂါ',
    'Epilepsy or seizure disorder': 'ဝက်ရူးပြန် သို့မဟုတ် တက်ခြင်းရောဂါ',
    'Familial high cholesterol': 'မျိုးရိုးလိုက် ကိုလက်စထရောမြင့်ခြင်း',
    'Hemophilia': 'သွေးမတိတ်ရောဂါ (Hemophilia)',
    'High blood pressure': 'သွေးတိုးရောဂါ',
    'Heart disease': 'နှလုံးရောဂါ',
    'Kidney disease': 'ကျောက်ကပ်ရောဂါ',
    'Muscular dystrophy': 'ကြွက်သားအားနည်းပျက်စီးရောဂါ',
    'Ovarian cancer': 'မျိုးဥအိမ်ကင်ဆာ',
    'Prostate cancer': 'ဆီးကျိတ်ကင်ဆာ',
    'Sickle cell disease': 'Sickle cell disease (မျိုးရိုးလိုက် သွေးရောဂါ)',
    'Stroke': 'လေဖြတ်ရောဂါ',
    'Thalassemia': 'သာလာဆီးမီးယား (Thalassemia)',
    'Thyroid cancer': 'သိုင်းရွိုက်ကင်ဆာ',
    'Other disease / not listed': 'စာရင်းတွင်မပါသော အခြားရောဂါ',
    'Back': 'နောက်သို့',
    'Edit': 'ပြင်ဆင်ရန်',
    'Review & Submit': 'ပြန်လည်စစ်ဆေးပြီး တင်သွင်းရန်',
    'Calculate Risk Assessment': 'အန္တရာယ်အကဲဖြတ်ချက် တွက်ချက်ရန်',
    'Assessment Results': 'အကဲဖြတ် ရလဒ်များ',
    'Summary of newborn risk indicators': 'မွေးကင်းစကလေး အန္တရာယ်ညွှန်းကိန်း အကျဉ်းချုပ်',
    'APGAR Score Breakdown': 'APGAR အမှတ် အသေးစိတ်',
    'Birth Summary': 'မွေးဖွားမှု အကျဉ်းချုပ်',
    'Birth Summary of the Newborn Baby': 'မွေးကင်းစကလေး၏ မွေးဖွားမှု အကျဉ်းချုပ်',
    'Gestational Age': 'ကိုယ်ဝန်ဆောင်ချိန်ကာလ (ပတ်)',
    'Remark': 'မှတ်ချက်',
    'Immediate Condition Risk': 'ချက်ချင်းအခြေအနေ အန္တရာယ်',
    'Birth-Related Monitoring': 'မွေးဖွားမှုဆိုင်ရာ စောင့်ကြည့်ခြင်း',
    'Family-History Follow-up': 'မိသားစုရာဇဝင် နောက်ဆက်တွဲစစ်ဆေးခြင်း',
    'Risk Index': 'အန္တရာယ်ညွှန်းကိန်း',
    'Level': 'အဆင့်',
    'View input membership graphs': 'Input membership graph များကြည့်ရန်',
    'Assessment Factors': 'အကဲဖြတ် အချက်များ',
    'Main Contributing Factors': 'အဓိက သက်ရောက်သည့်အချက်များ',
    'Lower-Impact Factors': 'သက်ရောက်မှုနည်းသော အချက်များ',
    'Important Triggered Fuzzy Rules': 'သက်ရောက်နေသော အရေးကြီး Fuzzy Rules',
    'Rule': 'စည်းမျဉ်း',
    'Name and description': 'အမည်နှင့် ရှင်းလင်းချက်',
    'Result': 'ရလဒ်',
    'Activation': 'သက်ရောက်မှု',
    'Recommended actions by module': 'ကဏ္ဍအလိုက် အကြံပြုလုပ်ဆောင်ချက်များ',
    'Immediate condition by observation time': 'စောင့်ကြည့်ချိန်အလိုက် ချက်ချင်းအခြေအနေ',
    'Inference inputs': 'တွက်ချက်ရာတွင် အသုံးပြုသော အချက်များ',
    'Recorded birth findings and final result': 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှုအချက်များနှင့် နောက်ဆုံးရလဒ်',
    'Reason for this result': 'ဤရလဒ် ဖြစ်ပေါ်ရသည့်အကြောင်းရင်း',
    'Monitoring concerns': 'စောင့်ကြည့်ရန် စိုးရိမ်ချက်များ',
    'Recommended monitoring actions': 'အကြံပြု စောင့်ကြည့်လုပ်ဆောင်ချက်များ',
    'Care concerns': 'စောင့်ရှောက်မှု စိုးရိမ်ချက်များ',
    'Recommended actions': 'အကြံပြု လုပ်ဆောင်ချက်များ',
    "Recorded observations describe the assessed times; they do not establish the baby's current condition or a diagnosis.": 'မှတ်တမ်းတင်ထားသော စောင့်ကြည့်ချက်များသည် စစ်ဆေးချိန်ရှိ အခြေအနေကိုသာ ဖော်ပြပြီး လက်ရှိအခြေအနေ သို့မဟုတ် ရောဂါအမည်ကို အတည်မပြုနိုင်ပါ။',
    'Download PDF Summary': 'PDF အကျဉ်းချုပ် ဒေါင်းလုဒ်ရန်',
    'View Saved Assessment': 'သိမ်းထားသော အကဲဖြတ်ချက် ကြည့်ရန်',
    'ML NICU Admission Research Estimate': 'ML NICU တက်ရောက်နိုင်ခြေ သုတေသန ခန့်မှန်းချက်',
    'Research estimate only': 'သုတေသန ခန့်မှန်းချက်သာ',
    'Model performance': 'Model စွမ်းဆောင်ရည်',
    'Metric': 'တိုင်းတာချက်',
    'Meaning': 'အဓိပ္ပာယ်',
    'Assessment History': 'အကဲဖြတ် မှတ်တမ်း',
    'All stored newborn assessments are shown here.': 'သိမ်းဆည်းထားသော မွေးကင်းစကလေး အကဲဖြတ်ချက်အားလုံးကို ဤနေရာတွင် ပြထားပါသည်။',
    'Filter by date': 'ရက်စွဲဖြင့် စစ်ထုတ်ရန်',
    "Child's name": 'ကလေးအမည်',
    'Search': 'ရှာဖွေရန်',
    'Clear filters': 'စစ်ထုတ်မှုများ ရှင်းရန်',
    'Date': 'ရက်စွဲ',
    'Baby': 'ကလေး',
    'Immediate action': 'ချက်ချင်း လုပ်ဆောင်ရန်',
    'View': 'ကြည့်ရန်',
    'No assessments match your search or date filter.': 'သင်ရှာဖွေထားသော အမည် သို့မဟုတ် ရက်စွဲနှင့် ကိုက်ညီသည့် အကဲဖြတ်ချက်မရှိပါ။',
    'No saved assessments yet.': 'သိမ်းဆည်းထားသော အကဲဖြတ်ချက် မရှိသေးပါ။',
    'My': 'ကျွန်ုပ်၏',
    'Profile': 'Profile',
    'Your account and per-baby assessment overview.': 'သင့်အကောင့်နှင့် ကလေးတစ်ဦးချင်း အကဲဖြတ်မှု အကျဉ်းချုပ်။',
    'Welcome back': 'ပြန်လည်ကြိုဆိုပါသည်',
    "Log in to complete a newborn's health risk assessment.": 'မွေးကင်းစကလေး ကျန်းမာရေးအန္တရာယ် အကဲဖြတ်ရန် ဝင်ရောက်ပါ။',
    'Email': 'အီးမေးလ်',
    'Password': 'စကားဝှက်',
    'Log in': 'ဝင်ရောက်ရန်',
    'No account yet?': 'အကောင့်မရှိသေးပါသလား။',
    'Create one': 'အကောင့်ဖွင့်ရန်',
    'Create your account': 'သင့်အကောင့် ဖန်တီးပါ',
    "Signup to save newborn's health risk assessments.": 'မွေးကင်းစကလေး ကျန်းမာရေးအန္တရာယ် အကဲဖြတ်ချက်များ သိမ်းဆည်းရန် အကောင့်ဖွင့်ပါ။',
    'Name': 'အမည်',
    'Confirm password': 'စကားဝှက် အတည်ပြုရန်',
    'Create account': 'အကောင့်ဖွင့်ရန်',
    'Already registered?': 'အကောင့်ရှိပြီးသားလား။'
  };

  const translatedAttributes = ['placeholder', 'title', 'aria-label'];
  const ignoredParents = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'CODE', 'PRE']);
  const warningPhrases = [
    'Heartbeat or breathing concern. Assess immediately.',
    'Blue/pale colour, absent reflex, or limp tone. Assess immediately.',
    'Reduced reflex or tone. Reassess clinically.',
    'Critical total. Assess immediately; do not delay care.',
    'APGAR below 7. Record the next 5-minute observation. Do not delay care.'
  ];

  function translatedText(value) {
    const trimmed = value.trim();
    if (translations[trimmed]) return translations[trimmed];
    let match = trimmed.match(/^Birth Summary of (.+)$/);
    if (match) return 'မွေးဖွားမှု အကျဉ်းချုပ် — ' + match[1];
    match = trimmed.match(/^(\d+)-minute observation$/);
    if (match) return match[1] + ' မိနစ် စောင့်ကြည့်ချက်';
    match = trimmed.match(/^Recorded total: (\d+)\/10\.$/);
    if (match) return 'မှတ်တမ်းတင်ထားသော စုစုပေါင်းအမှတ်: ' + match[1] + '/10။';
    match = trimmed.match(/^Low total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် နိမ့်သည် — ' + match[1] + '/10';
    match = trimmed.match(/^Moderately abnormal total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် အတန်အသင့် မူမမှန်ပါ — ' + match[1] + '/10';
    match = trimmed.match(/^Reassuring total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် စိတ်ချရသည် — ' + match[1] + '/10';
    let phraseTranslated = trimmed;
    warningPhrases.forEach(function (phrase) {
      phraseTranslated = phraseTranslated.split(phrase).join(translations[phrase]);
    });
    if (phraseTranslated !== trimmed) return phraseTranslated;
    return trimmed;
  }

  function translateTextNode(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return;
    if (node.parentElement && (ignoredParents.has(node.parentElement.tagName) || node.parentElement.isContentEditable)) return;
    const original = node.nodeValue;
    const trimmed = original.trim();
    const translated = translatedText(trimmed);
    if (translated === trimmed) return;
    node.nodeValue = original.replace(trimmed, translated);
  }

  function translateElement(element) {
    if (!(element instanceof Element)) return;
    translatedAttributes.forEach(function (attribute) {
      if (!element.hasAttribute(attribute)) return;
      const value = element.getAttribute(attribute);
      const translated = translatedText(value);
      if (translated !== value.trim()) element.setAttribute(attribute, translated);
    });
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) translateTextNode(node);
  }

  function translatePage() {
    document.documentElement.lang = 'my';
    translateElement(document.documentElement);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', translatePage, { once: true });
  } else {
    translatePage();
  }

  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.type === 'characterData') translateTextNode(mutation.target);
      mutation.addedNodes.forEach(function (node) {
        if (node.nodeType === Node.TEXT_NODE) translateTextNode(node);
        if (node.nodeType === Node.ELEMENT_NODE) translateElement(node);
      });
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    observer.observe(document.body, { childList: true, characterData: true, subtree: true });
  }, { once: true });
})();
