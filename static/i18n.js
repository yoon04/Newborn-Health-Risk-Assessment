(function () {
  'use strict';

  let activeLanguage = window.NHRA_LANGUAGE === 'my' ? 'my' : 'en';
  const originalText = new WeakMap();
  const originalAttributes = new WeakMap();

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
    'View input membership graphs': 'Input membership ဂရပ်များကို ကြည့်ရန်',
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
    'Immediate observation summary and final result': 'ချက်ချင်း စောင့်ကြည့်မှု အကျဉ်းချုပ်နှင့် နောက်ဆုံးရလဒ်',
    'Weak or irregular breathing': 'အသက်ရှူမှု အားနည်းခြင်း သို့မဟုတ် မမှန်ခြင်း',
    'No heartbeat detected': 'နှလုံးခုန်သံ မတွေ့ရှိပါ',
    'Heart rate below 100 bpm': 'နှလုံးခုန်နှုန်း 100 bpm အောက်ဖြစ်သည်',
    'No breathing detected': 'အသက်ရှူမှု မတွေ့ရှိပါ',
    'No reflex response to stimulation': 'လှုံ့ဆော်မှုကို တုံ့ပြန်မှုမရှိပါ',
    'Limited reflex response (grimace only)': 'တုံ့ပြန်မှု အကန့်အသတ်ရှိသည် (မျက်နှာရှုံ့ခြင်းသာ)',
    'Limp or absent muscle tone': 'ကြွက်သားတင်းအား မရှိ သို့မဟုတ် ပျော့ခွေနေသည်',
    'Reduced muscle tone (some flexion)': 'ကြွက်သားတင်းအား လျော့နည်းသည် (အနည်းငယ်ကွေးနိုင်)',
    'How the birth monitoring index was calculated': 'မွေးဖွားမှု စောင့်ကြည့်ညွှန်းကိန်း တွက်ချက်ပုံ',
    'Explanation': 'ရှင်းလင်းချက်',
    'Output': 'အထွက်ရလဒ်',
    'Back to Review & Edit': 'ပြန်လည်စစ်ဆေးပြီး ပြင်ဆင်ရန်',
    'Seek immediate assessment by the neonatal care team or emergency medical services. Do not wait to finish this form or for an APGAR total. Treatment requires direct clinical assessment.': 'မွေးကင်းစကလေး စောင့်ရှောက်ရေးအဖွဲ့ သို့မဟုတ် အရေးပေါ်ဆေးဘက်ဝန်ဆောင်မှုထံ ချက်ချင်း အကဲဖြတ်မှုခံယူပါ။ ဤ form ပြီးဆုံးသည်အထိ သို့မဟုတ် APGAR စုစုပေါင်းအမှတ်ရသည်အထိ မစောင့်ပါနှင့်။ ကုသမှုအတွက် တိုက်ရိုက်ဆေးဘက်စစ်ဆေးမှု လိုအပ်သည်။',
    'A High rule is active, but the combined index is below 70; recorded monitoring concerns still apply.': 'High rule တစ်ခု သက်ရောက်နေသော်လည်း ပေါင်းစပ်ညွှန်းကိန်းသည် 70 အောက်ဖြစ်သည်။ မှတ်တမ်းတင်ထားသော စောင့်ကြည့်ရန် စိုးရိမ်ချက်များသည် ဆက်လက်သက်ဆိုင်သည်။',
    'Rule activation is a membership strength, not a probability or a percentage contribution.': 'Rule activation သည် membership strength ဖြစ်ပြီး ဖြစ်နိုင်ခြေ သို့မဟုတ် ရာခိုင်နှုန်းပါဝင်မှု မဟုတ်ပါ။',
    'Use the local preterm/low-birth-weight pathway to document feeding support, thermal care, respiratory observations and growth follow-up; the clinical team decides interventions.': 'ဒေသဆိုင်ရာ လမစေ့မွေးဖွားမှု/မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းမှု လမ်းညွှန်အတိုင်း နို့တိုက်ကျွေးမှုအကူအညီ၊ ကိုယ်အပူချိန်ထိန်းသိမ်းမှု၊ အသက်ရှူမှုစောင့်ကြည့်ချက်နှင့် ကြီးထွားမှုနောက်ဆက်တွဲကို မှတ်တမ်းတင်ပါ။ လိုအပ်သော ကုသမှုကို ဆေးဘက်အဖွဲ့က ဆုံးဖြတ်ပါမည်။',
    'Review maternal medical history and antenatal findings as context; maternal age alone does not establish illness in the newborn or a need for treatment.': 'မိခင်၏ ဆေးမှတ်တမ်းနှင့် ကိုယ်ဝန်ဆောင်ကာလ တွေ့ရှိချက်များကို ဆက်စပ်အချက်အလက်အဖြစ် ပြန်လည်စစ်ဆေးပါ။ မိခင်အသက်တစ်ခုတည်းဖြင့် မွေးကင်းစကလေးတွင် ရောဂါရှိခြင်း သို့မဟုတ် ကုသရန်လိုခြင်းကို မသတ်မှတ်နိုင်ပါ။',
    'Delivery complication reported; its type and severity are not captured by this Yes/No input.': 'မွေးဖွားမှု ပြဿနာရှိကြောင်း မှတ်တမ်းတင်ထားသည်။ ဤ Yes/No input ဖြင့် အမျိုးအစားနှင့် ပြင်းထန်မှုကို မဖော်ပြနိုင်ပါ။',
    'Clarify the delivery complication and document a neonatal review and monitoring plan appropriate to the actual findings.': 'မွေးဖွားမှု ပြဿနာကို ရှင်းလင်းအတည်ပြုပြီး အမှန်တကယ်တွေ့ရှိချက်နှင့် ကိုက်ညီသော မွေးကင်းစကလေး စစ်ဆေးမှုနှင့် စောင့်ကြည့်အစီအစဉ်ကို မှတ်တမ်းတင်ပါ။',
    'No component safety alert is triggered by the latest recorded scores; continue direct clinical observation.': 'နောက်ဆုံးမှတ်တမ်းတင်ထားသော အမှတ်များအရ အချက်တစ်ခုချင်း၏ ဘေးကင်းရေးသတိပေးချက် မပေါ်ပါ။ တိုက်ရိုက်ဆေးဘက်စောင့်ကြည့်မှုကို ဆက်လုပ်ပါ။',
    'Earlier component concerns remain documented; improvement in the total does not confirm their clinical resolution.': 'အစောပိုင်း အချက်တစ်ခုချင်း၏ စိုးရိမ်ချက်များကို မှတ်တမ်းတွင် ဆက်ထားပါသည်။ စုစုပေါင်းအမှတ် တိုးတက်ခြင်းက ဆေးဘက်ဆိုင်ရာ ပြဿနာ ပြေလည်သွားကြောင်း မအတည်ပြုနိုင်ပါ။',
    "Recorded observations describe the assessed times; they do not establish the baby's current condition or a diagnosis.": 'မှတ်တမ်းတင်ထားသော စောင့်ကြည့်ချက်များသည် စစ်ဆေးချိန်ရှိ အခြေအနေကိုသာ ဖော်ပြပြီး လက်ရှိအခြေအနေ သို့မဟုတ် ရောဂါအမည်ကို အတည်မပြုနိုင်ပါ။',
    'Download PDF Summary': 'PDF အကျဉ်းချုပ် ဒေါင်းလုဒ်ရန်',
    'View Saved Assessment': 'သိမ်းထားသော အကဲဖြတ်ချက် ကြည့်ရန်',
    'ML NICU Admission Research Estimate': 'ML NICU တက်ရောက်နိုင်ခြေ သုတေသန ခန့်မှန်းချက်',
    'ML research estimate: recorded NICU admission': 'ML သုတေသန ခန့်မှန်းချက် — မှတ်တမ်းတင်ထားသော NICU တက်ရောက်မှု',
    'Research only · clinician review required': 'သုတေသနအတွက်သာ · ဆရာဝန် ပြန်လည်စစ်ဆေးရန် လိုအပ်သည်',
    'Estimated probability of recorded NICU admission': 'မှတ်တမ်းတင်ထားသော NICU တက်ရောက်နိုင်ခြေ ခန့်မှန်းချက်',
    'Separate research output': 'သီးခြား သုတေသနရလဒ်',
    'Model flow': 'Model လုပ်ဆောင်ပုံ',
    '3 recorded inputs': 'မှတ်တမ်းတင်ထားသော input ၃ ခု',
    'Calibrated model': 'ချိန်ညှိထားသော model',
    'Research estimate': 'သုတေသန ခန့်မှန်းချက်',
    'Research estimate only; observed findings and module rules guide the separate action summaries.': 'သုတေသန ခန့်မှန်းချက်သာဖြစ်သည်။ တွေ့ရှိချက်များနှင့် module rules များကို သီးခြားလုပ်ဆောင်ချက် အကျဉ်းချုပ်များအတွက် အသုံးပြုသည်။',
    'Gestational age used by ML': 'ML တွင် အသုံးပြုသော ကိုယ်ဝန်သက်တမ်း',
    'Birth weight used': 'အသုံးပြုသော မွေးဖွားချိန် ကိုယ်အလေးချိန်',
    'Maternal age used': 'အသုံးပြုသော မိခင်အသက်',
    'Model': 'Model',
    'Historical evaluation metrics': 'ယခင်ဒေတာဖြင့် အကဲဖြတ်ထားသော တိုင်းတာချက်များ',
    'Area Under the Receiver Operating Characteristic Curve': 'Receiver Operating Characteristic Curve အောက်ရှိ ဧရိယာ',
    'Area Under the Precision-Recall Curve': 'Precision-Recall Curve အောက်ရှိ ဧရိယာ',
    'Probability prediction error score (not an abbreviation)': 'ဖြစ်နိုင်ခြေ ခန့်မှန်းမှု အမှားအယွင်းအမှတ် (အတိုကောက် မဟုတ်ပါ)',
    'How well the model separates admissions from non-admissions across thresholds. Higher is better; 0.5 is similar to chance and 1.0 is perfect separation.': 'သတ်မှတ်တန်ဖိုးအမျိုးမျိုးတွင် တက်ရောက်မှုနှင့် မတက်ရောက်မှုကို model က မည်မျှကောင်းစွာ ခွဲခြားနိုင်သည်ကို ဖော်ပြသည်။ တန်ဖိုးမြင့်လေ ကောင်းလေဖြစ်ပြီး 0.5 သည် ကျပန်းခန့်မှန်းမှုနှင့် ဆင်တူကာ 1.0 သည် ပြည့်စုံသော ခွဲခြားမှုဖြစ်သည်။',
    'Summarizes precision and recall for the admission outcome. Higher is better, but the value depends on how common admissions are in the evaluation data.': 'တက်ရောက်မှုရလဒ်အတွက် precision နှင့် recall ကို အကျဉ်းချုပ်ဖော်ပြသည်။ တန်ဖိုးမြင့်လေ ကောင်းလေဖြစ်သော်လည်း အကဲဖြတ်ဒေတာထဲတွင် တက်ရောက်မှု မည်မျှများသည်ပေါ် မူတည်သည်။',
    'The average squared difference between predicted probabilities and recorded outcomes. Lower is better; 0 means perfect probability predictions.': 'ခန့်မှန်းထားသော ဖြစ်နိုင်ခြေနှင့် မှတ်တမ်းတင်ရလဒ်တို့ကြား ကွာခြားချက်၏ ပျမ်းမျှနှစ်ထပ်ကိန်းဖြစ်သည်။ တန်ဖိုးနိမ့်လေ ကောင်းလေဖြစ်ပြီး 0 သည် ပြည့်စုံသော ဖြစ်နိုင်ခြေခန့်မှန်းမှုဖြစ်သည်။',
    'Important: A low estimate cannot establish that a baby is safe. APGAR component alerts and all three module actions remain independent.': 'အရေးကြီးချက်: ခန့်မှန်းတန်ဖိုးနိမ့်ခြင်းဖြင့် ကလေးဘေးကင်းကြောင်း အတည်မပြုနိုင်ပါ။ APGAR အချက်သတိပေးချက်များနှင့် module သုံးခု၏ လုပ်ဆောင်ချက်များသည် သီးခြားဖြစ်သည်။',
    'Model scope, evidence, and limitations': 'Model အသုံးပြုနိုင်သည့် နယ်ပယ်၊ အထောက်အထားနှင့် ကန့်သတ်ချက်များ',
    'Inputs do not include APGAR components, delivery complications, or family history. No individual uncertainty interval or clinical risk category is assigned.': 'Input များတွင် APGAR အချက်များ၊ မွေးဖွားမှု ပြဿနာများ သို့မဟုတ် မိသားစုရာဇဝင် မပါဝင်ပါ။ တစ်ဦးချင်း မသေချာမှုအပိုင်းအခြား သို့မဟုတ် ဆေးဘက်ဆိုင်ရာ အန္တရာယ်အမျိုးအစား မသတ်မှတ်ထားပါ။',
    'CDC birth-data source': 'CDC မွေးဖွားမှုဒေတာ ရင်းမြစ်',
    'CDC gestation format': 'CDC ကိုယ်ဝန်သက်တမ်း format',
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

  Object.assign(translations, {
    'Low': 'နိမ့်',
    'Moderate': 'အလယ်အလတ်',
    'High': 'မြင့်',
    'Urgent evaluation': 'အရေးပေါ် အကဲဖြတ်ရန်',
    'Monitoring plan': 'စောင့်ကြည့်ရေး အစီအစဉ်',
    'Routine birth follow-up': 'ပုံမှန် မွေးဖွားမှု နောက်ဆက်တွဲစစ်ဆေးခြင်း',
    'Prompt neonatal monitoring review': 'မွေးကင်းစကလေး စောင့်ကြည့်မှုကို အမြန်ပြန်လည်စစ်ဆေးရန်',
    'Extremely preterm': 'အလွန်လမစေ့မွေးဖွားမှု',
    'Very preterm': 'လွန်စွာလမစေ့မွေးဖွားမှု',
    'Preterm': 'လမစေ့မွေးဖွားမှု',
    'Early term': 'လစေ့အစောပိုင်း မွေးဖွားမှု',
    'Full term': 'လစေ့မွေးဖွားမှု',
    'Late term': 'လစေ့နောက်ကျ မွေးဖွားမှု',
    'Post-term': 'လွန်လမွေးဖွားမှု',
    'Extremely low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်နည်း',
    'Very low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်နည်း',
    'Low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်း',
    'Not low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် မနည်းပါ',
    'Higher birth weight (project review threshold)': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်မြင့် (project ပြန်လည်စစ်ဆေးမှု သတ်မှတ်ချက်)',
    'Reported': 'မှတ်တမ်းတင်ထားသည်',
    'Not reported': 'မမှတ်တမ်းတင်ထားပါ'
  });

  Object.assign(translations, {
    'Very preterm gestation': 'လွန်စွာလမစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Very high birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်မြင့်',
    'Very advanced maternal-age context': 'မိခင်အသက် အလွန်မြင့်သည့် ဆက်စပ်အခြေအနေ',
    'Preterm with low birth weight': 'လမစေ့မွေးဖွားမှုနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းမှု',
    'Post-term with high birth weight': 'လွန်လမွေးဖွားမှုနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်မြင့်မှု',
    'Complication with a birth concern': 'မွေးဖွားမှု စိုးရိမ်ချက်နှင့် နောက်ဆက်တွဲပြဿနာ',
    'Preterm gestation': 'လမစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Post-term gestation': 'လွန်လ ကိုယ်ဝန်သက်တမ်း',
    'High birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်မြင့်',
    'Young maternal-age context': 'မိခင်အသက်ငယ်သည့် ဆက်စပ်အခြေအနေ',
    'Advanced maternal-age context': 'မိခင်အသက်မြင့်သည့် ဆက်စပ်အခြေအနေ',
    'Reported delivery complication': 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာ',
    'Term, normal weight, no complication': 'လစေ့၊ ပုံမှန်ကိုယ်အလေးချိန်၊ ပြဿနာမရှိ',
    'Brier score': 'Brier score',
    'Reference:': 'ရည်ညွှန်းချက်:',
    'Estimate unavailable': 'ခန့်မှန်းချက် မရရှိနိုင်ပါ',
    'A low estimate cannot establish that a baby is safe. APGAR component alerts and all three module actions remain independent.': 'ခန့်မှန်းတန်ဖိုးနိမ့်ခြင်းဖြင့် ကလေးဘေးကင်းကြောင်း အတည်မပြုနိုင်ပါ။ APGAR အချက်သတိပေးချက်များနှင့် module သုံးခု၏ လုပ်ဆောင်ချက်များသည် သီးခြားဖြစ်သည်။',
    'Model trained on 2024 U.S. records and evaluated unchanged on 2023 records.': 'Model ကို 2024 U.S. မှတ်တမ်းများဖြင့် လေ့ကျင့်ပြီး ပြောင်းလဲမှုမရှိဘဲ 2023 မှတ်တမ်းများဖြင့် အကဲဖြတ်ထားသည်။',
    '+ Add another disease': '+ နောက်ထပ်ရောဂါ ထည့်ရန်'
  });

  Object.assign(translations, {
    'male': 'ကျား',
    'female': 'မ',
    'yes': 'ရှိ',
    'no': 'မရှိ',
    'Singleton': 'တစ်ဦးတည်း မွေးဖွားမှု',
    'Twins': 'အမွှာမွေးဖွားမှု',
    'Other multiple birth': 'အခြားအမြွှာမွေးဖွားမှု',
    'No known disease': 'သိရှိထားသော ရောဂါမရှိပါ',
    'Assessment identity': 'အကဲဖြတ်မည့် ကလေး',
    'Other twin (separate assessment needed)': 'အခြားအမွှာ (သီးခြားအကဲဖြတ်ရန် လိုအပ်သည်)',
    'Immediate inference reference': 'ချက်ချင်းအခြေအနေ တွက်ချက်ရာတွင် အသုံးပြုသော စောင့်ကြည့်ချက်',
    "This assessment will be saved in shared history under the baby's name.": 'ဤအကဲဖြတ်ချက်ကို ကလေးအမည်ဖြင့် မျှဝေမှတ်တမ်းတွင် သိမ်းဆည်းပါမည်။'
  });

  Object.assign(translations, {
    'Closer monitoring and professional review': 'ပိုမိုနီးကပ်စွာ စောင့်ကြည့်ပြီး ကျန်းမာရေးပညာရှင် ပြန်လည်စစ်ဆေးရန်',
    'Routine care and observation': 'ပုံမှန်စောင့်ရှောက်မှုနှင့် စောင့်ကြည့်မှု',
    'Professional review': 'ကျန်းမာရေးပညာရှင် ပြန်လည်စစ်ဆေးရန်',
    'Routine observation': 'ပုံမှန် စောင့်ကြည့်မှု',
    'Arrange neonatal professional review and a monitoring plan for the immediate or birth-related concerns.': 'ချက်ချင်းအခြေအနေ သို့မဟုတ် မွေးဖွားမှုဆိုင်ရာ စိုးရိမ်ချက်များအတွက် မွေးကင်းစကလေး ကျန်းမာရေးပညာရှင် ပြန်လည်စစ်ဆေးမှုနှင့် စောင့်ကြည့်အစီအစဉ်ကို စီစဉ်ပါ။',
    'Continue routine newborn care and observation; seek professional help for new symptoms.': 'ပုံမှန် မွေးကင်းစကလေး စောင့်ရှောက်မှုနှင့် စောင့်ကြည့်မှုကို ဆက်လက်လုပ်ဆောင်ပြီး လက္ခဏာအသစ်များရှိလာပါက ကျန်းမာရေးပညာရှင်ထံ အကူအညီတောင်းပါ။',
    'Seek urgent professional evaluation of the baby’s current condition.': 'ကလေး၏ လက်ရှိအခြေအနေကို ကျန်းမာရေးပညာရှင်ထံ အရေးပေါ် စစ်ဆေးပါ။',
    'A delivery complication was reported; review it with the recorded APGAR findings.': 'မွေးဖွားမှု ပြဿနာရှိကြောင်း မှတ်တမ်းတင်ထားသည်။ မှတ်တမ်းတင်ထားသော APGAR တွေ့ရှိချက်များနှင့်အတူ ပြန်လည်စစ်ဆေးပါ။',
    'Have the neonatal clinician reassess this component and document the finding.': 'မွေးကင်းစကလေး ဆရာဝန်အား ဤအချက်ကို ပြန်လည်စစ်ဆေးစေပြီး တွေ့ရှိချက်ကို မှတ်တမ်းတင်ပါ။',
    'Prematurity and maternal medication can affect tone and reflex responses; this notice does not diagnose a condition or prescribe treatment.': 'လမစေ့မွေးဖွားမှုနှင့် မိခင်သောက်သုံးသော ဆေးဝါးများသည် ကြွက်သားတင်းအားနှင့် တုံ့ပြန်မှုကို သက်ရောက်နိုင်သည်။ ဤသတိပေးချက်သည် ရောဂါအမည်သတ်မှတ်ခြင်း သို့မဟုတ် ကုသမှုညွှန်ကြားခြင်း မဟုတ်ပါ။',
    'Seek immediate in-person clinical assessment if this describes the baby now. Do not wait for an APGAR total.': 'ဤအချက်သည် ကလေး၏ လက်ရှိအခြေအနေကို ဖော်ပြပါက လူကိုယ်တိုင် ဆေးဘက်စစ်ဆေးမှု ချက်ချင်းခံယူပါ။ APGAR စုစုပေါင်းအမှတ်ကို မစောင့်ပါနှင့်။',
    'This notice raises the triage recommendation independently of the fuzzy index; it does not prescribe treatment.': 'ဤသတိပေးချက်သည် fuzzy index နှင့် သီးခြားအနေဖြင့် triage အကြံပြုချက်ကို မြှင့်တင်သော်လည်း ကုသမှုကို မညွှန်ကြားပါ။',
    'APGAR is the main signal. A reported complication raises concern most strongly when APGAR is already concerning.': 'APGAR သည် အဓိကညွှန်းကိန်းဖြစ်သည်။ APGAR စိုးရိမ်ရပြီးသားအချိန်တွင် မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာက စိုးရိမ်မှုကို အများဆုံး မြှင့်တင်သည်။',
    'This module uses gestational age, birth weight, maternal age, and delivery information with overlapping fuzzy memberships.': 'ဤ module သည် ကိုယ်ဝန်သက်တမ်း၊ မွေးဖွားချိန် ကိုယ်အလေးချိန်၊ မိခင်အသက်နှင့် မွေးဖွားမှုအချက်အလက်များကို ထပ်နေသော fuzzy memberships များဖြင့် အသုံးပြုသည်။',
    'Reference: latest complete 5-minute observation.': 'ရည်ညွှန်းချက်: နောက်ဆုံးပြည့်စုံသော ၅ မိနစ် စောင့်ကြည့်ချက်။',
    'View rule explanations and assessment factors': 'Rule ရှင်းလင်းချက်များနှင့် အကဲဖြတ်အချက်များ ကြည့်ရန်',
    'Rule clarity basis (heuristic) · Immediate module': 'Rule ရှင်းလင်းမှုအခြေခံ (heuristic) · ချက်ချင်းအခြေအနေ module',
    'Activation strength is shown on a 0 to 1 scale. It is not a contribution percentage.': 'Activation strength ကို 0 မှ 1 အတိုင်းအတာဖြင့် ပြထားသည်။ ပါဝင်မှုရာခိုင်နှုန်း မဟုတ်ပါ။',
    'Note:': 'မှတ်ချက်:',
    'This is not a clinical diagnosis. Please consult a healthcare professional for medical decisions.': 'ဤရလဒ်သည် ဆေးဘက်ဆိုင်ရာ ရောဂါသတ်မှတ်ချက် မဟုတ်ပါ။ ဆေးဘက်ဆုံးဖြတ်ချက်များအတွက် ကျန်းမာရေးပညာရှင်နှင့် တိုင်ပင်ပါ။'
  });

  Object.assign(translations, {
    'Follow-up': 'နောက်ဆက်တွဲစစ်ဆေးခြင်း',
    'of 100': '100 အနက်',
    'Risk Index:': 'အန္တရာယ်ညွှန်းကိန်း:',
    'Level:': 'အဆင့်:',
    'Reported family-history details': 'မှတ်တမ်းတင်ထားသော မိသားစုရာဇဝင် အသေးစိတ်',
    'Who has it': 'မည်သူတွင် ရှိသနည်း',
    'Indicator': 'ညွှန်းကိန်း',
    "Baby's APGAR Score": 'ကလေး၏ APGAR အမှတ်',
    'Gestational Age': 'ကိုယ်ဝန်သက်တမ်း',
    'Birth Weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်',
    "Mother's Age": 'မိခင်အသက်',
    'Family-History Indicator': 'မိသားစုရာဇဝင် ညွှန်းကိန်း',
    'Actions come from recorded findings and project rules and require clinician review. The ML research estimate does not change these actions. No combined overall risk score is calculated.': 'လုပ်ဆောင်ချက်များသည် မှတ်တမ်းတင်ထားသော တွေ့ရှိချက်များနှင့် project rules များမှ ရရှိပြီး ဆရာဝန်၏ ပြန်လည်စစ်ဆေးမှု လိုအပ်သည်။ ML သုတေသနခန့်မှန်းချက်က ဤလုပ်ဆောင်ချက်များကို မပြောင်းလဲပါ။ အားလုံးပေါင်းစပ်ထားသော အန္တရာယ်အမှတ်ကို မတွက်ချက်ပါ။',
    'Immediate condition': 'ချက်ချင်းအခြေအနေ',
    'Birth-related monitoring': 'မွေးဖွားမှုဆိုင်ရာ စောင့်ကြည့်ခြင်း',
    'Family-history follow-up': 'မိသားစုရာဇဝင် နောက်ဆက်တွဲစစ်ဆေးခြင်း',
    'Family-history plan': 'မိသားစုရာဇဝင် အစီအစဉ်',
    'Share the reported condition and affected relatives with the baby’s clinician. Discuss whether genetic counselling or disease-specific screening is appropriate; family history alone does not diagnose the baby.': 'မှတ်တမ်းတင်ထားသော ရောဂါနှင့် ရောဂါရှိသည့် ဆွေမျိုးများအကြောင်းကို ကလေးဆရာဝန်အား ပြောပြပါ။ မျိုးရိုးဗီဇဆိုင်ရာ ဆွေးနွေးအကြံပေးမှု သို့မဟုတ် ရောဂါအလိုက် စစ်ဆေးမှု လိုအပ်မလို ဆွေးနွေးပါ။ မိသားစုရာဇဝင်တစ်ခုတည်းဖြင့် ကလေးတွင် ရောဂါရှိကြောင်း မသတ်မှတ်နိုင်ပါ။',
    'Clarify family history with relatives and the baby’s clinician. Unknown history does not establish low inherited risk.': 'မိသားစုရာဇဝင်ကို ဆွေမျိုးများနှင့် ကလေးဆရာဝန်ထံ မေးမြန်းအတည်ပြုပါ။ ရာဇဝင်မသိရှိခြင်းသည် မျိုးရိုးလိုက်အန္တရာယ် နိမ့်ကြောင်း မဆိုလိုပါ။',
    'No additional referral is suggested by the reported family history alone. Continue routine newborn screening and share any newly discovered history with the clinician.': 'မှတ်တမ်းတင်ထားသော မိသားစုရာဇဝင်တစ်ခုတည်းအရ ထပ်ဆင့်လွှဲပြောင်းစစ်ဆေးရန် မလိုအပ်ပါ။ ပုံမှန်မွေးကင်းစကလေး စစ်ဆေးမှုကို ဆက်လုပ်ပြီး အသစ်သိရှိလာသော ရာဇဝင်ကို ဆရာဝန်အား ပြောပြပါ။',
    'Singleton births; gestation encoded as 20–45 completed weeks, weight 227–5999 g, maternal age 13–49 years.': 'တစ်ဦးတည်းမွေးဖွားမှုများအတွက် ကိုယ်ဝန်သက်တမ်း 20–45 ပတ်၊ ကိုယ်အလေးချိန် 227–5999 g နှင့် မိခင်အသက် 13–49 နှစ်အဖြစ် သတ်မှတ်အသုံးပြုထားသည်။',
    'Retrospective prediction of admission recorded on U.S. birth certificates; prediction timing is unverified.': 'U.S. မွေးစာရင်းများတွင် မှတ်တမ်းတင်ထားသော တက်ရောက်မှုကို ယခင်ဒေတာဖြင့် နောက်ကြောင်းပြန် ခန့်မှန်းထားခြင်းဖြစ်ပြီး ခန့်မှန်းချိန်ကို အတည်မပြုရသေးပါ။',
    '2023 historical evaluation is not local hospital or future-year validation.': '2023 ယခင်ဒေတာ အကဲဖြတ်မှုသည် ဒေသခံဆေးရုံဒေတာ သို့မဟုတ် နောင်နှစ်ဒေတာဖြင့် အတည်ပြုထားခြင်း မဟုတ်ပါ။',
    'At research threshold 0.10, sensitivity was 53.8% overall and 10.2% for term births. A low estimate cannot establish safety.': 'သုတေသန threshold 0.10 တွင် sensitivity သည် အားလုံးအတွက် 53.8% နှင့် လစေ့မွေးဖွားမှုများအတွက် 10.2% ဖြစ်သည်။ ခန့်မှန်းတန်ဖိုးနိမ့်ခြင်းဖြင့် ဘေးကင်းကြောင်း မအတည်ပြုနိုင်ပါ။',
    'No clinical action threshold is approved. This estimate does not determine admission, treatment, discharge, or module actions.': 'ဆေးဘက်လုပ်ဆောင်မှု threshold ကို အတည်ပြုထားခြင်း မရှိပါ။ ဤခန့်မှန်းချက်ဖြင့် ဆေးရုံတက်ခြင်း၊ ကုသခြင်း၊ ဆေးရုံဆင်းခြင်း သို့မဟုတ် module လုပ်ဆောင်ချက်များကို မဆုံးဖြတ်ပါ။',
    'All important inputs were complete and valid.': 'အရေးကြီးသော input အားလုံး ပြည့်စုံပြီး မှန်ကန်ပါသည်။',
    'One or more important inputs were incomplete.': 'အရေးကြီးသော input တစ်ခု သို့မဟုတ် တစ်ခုထက်ပို၍ မပြည့်စုံပါ။',
    'Family-history information was either specified or no condition was reported.': 'မိသားစုရာဇဝင်အချက်အလက်ကို ဖော်ပြထားပြီးဖြစ်သည် သို့မဟုတ် ရောဂါမရှိကြောင်း မှတ်တမ်းတင်ထားသည်။',
    'At least one family-history inheritance pattern was marked unknown.': 'မိသားစုရာဇဝင် မျိုးရိုးဆက်ခံမှုပုံစံ အနည်းဆုံးတစ်ခုကို မသိရှိဟု သတ်မှတ်ထားသည်။',
    'The strongest module fuzzy level was clearly separated from the alternatives.': 'အပြင်းဆုံး module fuzzy အဆင့်သည် အခြားအဆင့်များနှင့် ရှင်းလင်းစွာ ကွာခြားနေသည်။',
    'The module fuzzy levels showed a usable but not strong separation.': 'Module fuzzy အဆင့်များသည် အသုံးပြုနိုင်သည့် ကွာခြားမှုရှိသော်လည်း အလွန်မပြတ်သားပါ။',
    'The module fuzzy levels overlapped substantially, so the interpretation is less certain.': 'Module fuzzy အဆင့်များ အတော်အတန် ထပ်နေသဖြင့် ရှင်းလင်းဖော်ပြမှု မသေချာမှု ပိုများသည်။',
    'This is heuristic immediate-rule clarity, not calibrated uncertainty, predictive accuracy or a probability. A safety override can make the rule separation High without establishing model validity.': 'ဤအချက်သည် heuristic ချက်ချင်း rule ရှင်းလင်းမှုသာဖြစ်ပြီး ချိန်ညှိထားသော မသေချာမှု၊ ခန့်မှန်းတိကျမှု သို့မဟုတ် ဖြစ်နိုင်ခြေ မဟုတ်ပါ။ ဘေးကင်းရေး override ကြောင့် model မှန်ကန်မှုကို မအတည်ပြုဘဲ rule separation ကို High ဖြစ်စေနိုင်သည်။',
    'Stable APGAR pattern': 'တည်ငြိမ်သော APGAR ပုံစံ',
    'Concerning APGAR pattern': 'စိုးရိမ်ရသော APGAR ပုံစံ',
    'Critical APGAR pattern': 'အရေးကြီးသော APGAR ပုံစံ',
    'The APGAR memberships lean toward the stable range.': 'APGAR membership များသည် တည်ငြိမ်သော အပိုင်းသို့ ဦးတည်နေသည်။',
    'The APGAR memberships lean toward the concerning range.': 'APGAR membership များသည် စိုးရိမ်ရသော အပိုင်းသို့ ဦးတည်နေသည်။',
    'The APGAR memberships lean toward the critical range.': 'APGAR membership များသည် အရေးကြီးသော အပိုင်းသို့ ဦးတည်နေသည်။',
    'Term gestational age': 'လစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Preterm gestational age': 'လမစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Very preterm gestational age': 'အလွန်လမစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Post-term gestational age': 'လွန်ကဲ ကိုယ်ဝန်သက်တမ်း',
    'Gestational-age membership is strongest in the term set.': 'ကိုယ်ဝန်သက်တမ်း membership သည် လစေ့အုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Gestational-age membership is strongest in the preterm set.': 'ကိုယ်ဝန်သက်တမ်း membership သည် လမစေ့အုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Gestational-age membership is strongest in the very preterm set.': 'ကိုယ်ဝန်သက်တမ်း membership သည် အလွန်လမစေ့အုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Gestational-age membership is strongest in the post-term set.': 'ကိုယ်ဝန်သက်တမ်း membership သည် လွန်ကဲအုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Normal birth weight': 'ပုံမှန် မွေးဖွားချိန် ကိုယ်အလေးချိန်',
    'Low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းခြင်း',
    'Very low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်နည်းခြင်း',
    'Extremely low birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်အမင်းနည်းခြင်း',
    'High birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်များခြင်း',
    'Very high birth weight': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်များခြင်း',
    'Birth-weight membership is strongest in the normal set.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် membership သည် ပုံမှန်အုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Birth-weight membership is strongest in the low set.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် membership သည် နည်းသောအုပ်စုတွင် အပြင်းဆုံးဖြစ်သည်။',
    'Typical maternal age range': 'ပုံမှန် မိခင်အသက်အပိုင်းအခြား',
    'Typical maternal age adds no adverse-age activation; reassuring newborn rules depend on gestation, weight and complication findings.': 'ပုံမှန် မိခင်အသက်သည် ဆိုးကျိုးဖြစ်စေသော age activation မတိုးစေပါ။ စိတ်ချရသော မွေးကင်းစကလေး rules များသည် ကိုယ်ဝန်သက်တမ်း၊ ကိုယ်အလေးချိန်နှင့် မွေးဖွားမှု ပြဿနာတွေ့ရှိချက်များပေါ် မူတည်သည်။',
    'Reported delivery complication': 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာ',
    'A delivery complication was reported separately from delivery type.': 'မွေးဖွားမှုနည်းလမ်းနှင့် သီးခြားစီ မွေးဖွားမှု ပြဿနာရှိကြောင်း မှတ်တမ်းတင်ထားသည်။',
    'Stable APGAR with complication': 'ပြဿနာရှိသော်လည်း တည်ငြိမ်သော APGAR',
    'A reported delivery complication can elevate immediate risk even when APGAR is stable.': 'APGAR တည်ငြိမ်နေသော်လည်း မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာက ချက်ချင်းအန္တရာယ်ကို မြှင့်တင်နိုင်သည်။',
    'Concerning APGAR': 'စိုးရိမ်ရသော APGAR',
    'A concerning APGAR activates the moderate immediate risk level.': 'စိုးရိမ်ရသော APGAR က အလယ်အလတ် ချက်ချင်းအန္တရာယ်အဆင့်ကို သက်ရောက်စေသည်။',
    'Concerning APGAR with complication': 'ပြဿနာနှင့်အတူ စိုးရိမ်ရသော APGAR',
    'Concerning APGAR together with a reported delivery complication activates high immediate risk.': 'စိုးရိမ်ရသော APGAR နှင့် မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာတို့က မြင့်မားသော ချက်ချင်းအန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Complication with a birth concern': 'မွေးဖွားမှုဆိုင်ရာ စိုးရိမ်ချက်နှင့်အတူ ပြဿနာရှိခြင်း',
    'A reported delivery complication combines with gestational-age or weight concerns; maternal age alone does not activate this high rule.': 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာသည် ကိုယ်ဝန်သက်တမ်း သို့မဟုတ် ကိုယ်အလေးချိန် စိုးရိမ်ချက်နှင့် ပေါင်းစပ်သက်ရောက်သည်။ မိခင်အသက်တစ်ခုတည်းဖြင့် ဤ High rule မသက်ရောက်ပါ။',
    'A reported delivery complication activates moderate birth-related risk.': 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာက အလယ်အလတ် မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Low birth weight activates moderate birth-related risk.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းခြင်းက အလယ်အလတ် မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Father affected': 'ဖခင်တွင် ရောဂါရှိသည်',
    'Mother affected': 'မိခင်တွင် ရောဂါရှိသည်',
    'Both parents affected': 'မိဘနှစ်ဦးလုံးတွင် ရောဂါရှိသည်',
    'A known disease in the father elevates the family-history indicator.': 'ဖခင်တွင် သိရှိထားသော ရောဂါရှိခြင်းက မိသားစုရာဇဝင်ညွှန်းကိန်းကို မြှင့်တင်သည်။',
    'A known disease in the mother elevates the family-history indicator.': 'မိခင်တွင် သိရှိထားသော ရောဂါရှိခြင်းက မိသားစုရာဇဝင်ညွှန်းကိန်းကို မြှင့်တင်သည်။',
    'A known disease affecting both parents creates a stronger family-history indicator.': 'မိဘနှစ်ဦးလုံးတွင် သိရှိထားသော ရောဂါရှိခြင်းက ပိုမိုအားကောင်းသော မိသားစုရာဇဝင်ညွှန်းကိန်းကို ဖြစ်စေသည်။',
    'No known family disease': 'သိရှိထားသော မိသားစုရောဂါ မရှိပါ',
    'No known family disease supports a low family-history contribution.': 'သိရှိထားသော မိသားစုရောဂါမရှိခြင်းက မိသားစုရာဇဝင် သက်ရောက်မှုနိမ့်ခြင်းကို ပံ့ပိုးသည်။',
    'Family history unknown - low component': 'မိသားစုရာဇဝင် မသိရှိခြင်း — နိမ့်သောအချက်',
    'Family history unknown - uncertain component': 'မိသားစုရာဇဝင် မသိရှိခြင်း — မသေချာသောအချက်',
    'Unknown family history keeps a smaller low contribution because no affected relative is confirmed.': 'ရောဂါရှိသော ဆွေမျိုးကို အတည်မပြုနိုင်သဖြင့် မိသားစုရာဇဝင်မသိရှိမှုတွင် နိမ့်သောသက်ရောက်မှု အနည်းငယ် ဆက်ရှိသည်။',
    'Unknown family history activates a moderate contribution and lowers assessment confidence.': 'မိသားစုရာဇဝင် မသိရှိခြင်းက အလယ်အလတ်သက်ရောက်မှုကို ဖြစ်စေပြီး အကဲဖြတ်မှု ယုံကြည်စိတ်ချရမှုကို လျော့စေသည်။',
    'Other family member affected': 'အခြားမိသားစုဝင်တွင် ရောဂါရှိသည်',
    'Affected relative unknown': 'ရောဂါရှိသော ဆွေမျိုးကို မသိရှိပါ',
    'A known disease in another family member creates a smaller moderate contribution.': 'အခြားမိသားစုဝင်တွင် သိရှိထားသော ရောဂါရှိခြင်းက ပိုနည်းသော အလယ်အလတ်သက်ရောက်မှုကို ဖြစ်စေသည်။',
    'A known disease with an unknown affected relative creates an uncertain moderate contribution.': 'ရောဂါရှိသော ဆွေမျိုးကို မသိရှိသည့် ရောဂါမှတ်တမ်းက မသေချာသော အလယ်အလတ်သက်ရောက်မှုကို ဖြစ်စေသည်။',
    'Stable APGAR without complication': 'ပြဿနာမရှိသော တည်ငြိမ်သည့် APGAR',
    'Stable APGAR and no reported delivery complication support a low immediate risk level.': 'APGAR တည်ငြိမ်ပြီး မွေးဖွားမှု ပြဿနာမရှိကြောင်း မှတ်တမ်းတင်ထားခြင်းက နိမ့်သော ချက်ချင်းအန္တရာယ်အဆင့်ကို ပံ့ပိုးသည်။',
    'Critical APGAR': 'အရေးကြီးသော APGAR',
    'A critical APGAR activates the high immediate risk level.': 'အရေးကြီးသော APGAR က မြင့်မားသော ချက်ချင်းအန္တရာယ်အဆင့်ကို သက်ရောက်စေသည်။',
    'Preterm gestation': 'လမစေ့ ကိုယ်ဝန်သက်တမ်း',
    'Post-term gestation': 'လွန်ကဲ ကိုယ်ဝန်သက်တမ်း',
    'Preterm gestational age activates moderate birth-related risk.': 'လမစေ့ ကိုယ်ဝန်သက်တမ်းက အလယ်အလတ် မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Post-term gestational age activates moderate birth-related risk.': 'လွန်ကဲ ကိုယ်ဝန်သက်တမ်းက အလယ်အလတ် မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Very preterm gestational age activates high birth-related risk.': 'အလွန်လမစေ့ ကိုယ်ဝန်သက်တမ်းက မြင့်မားသော မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Extremely low birth weight activates high birth-related risk.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်အမင်းနည်းခြင်းက မြင့်မားသော မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Very low birth weight activates high birth-related risk.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်နည်းခြင်းက မြင့်မားသော မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Very high birth weight activates high birth-related risk.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန် အလွန်များခြင်းက မြင့်မားသော မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Preterm with low birth weight': 'လမစေ့ခြင်းနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းခြင်း',
    'Post-term with high birth weight': 'လွန်ကဲခြင်းနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်များခြင်း',
    'Preterm gestation together with low birth weight elevates birth-related risk.': 'လမစေ့ ကိုယ်ဝန်သက်တမ်းနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်နည်းခြင်းတို့က မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို မြှင့်တင်သည်။',
    'Post-term gestation together with high birth weight elevates birth-related risk.': 'လွန်ကဲ ကိုယ်ဝန်သက်တမ်းနှင့် မွေးဖွားချိန် ကိုယ်အလေးချိန်များခြင်းတို့က မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို မြှင့်တင်သည်။',
    'High birth weight activates moderate birth-related risk.': 'မွေးဖွားချိန် ကိုယ်အလေးချိန်များခြင်းက အလယ်အလတ် မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို သက်ရောက်စေသည်။',
    'Term, normal weight, no complication': 'လစေ့၊ ပုံမှန်ကိုယ်အလေးချိန်၊ ပြဿနာမရှိ',
    'Term gestation, normal birth weight, and no reported complication support low birth-related risk.': 'လစေ့ကိုယ်ဝန်သက်တမ်း၊ ပုံမှန်မွေးဖွားချိန် ကိုယ်အလေးချိန်နှင့် ပြဿနာမရှိခြင်းတို့က နိမ့်သော မွေးဖွားမှုဆိုင်ရာ အန္တရာယ်ကို ပံ့ပိုးသည်။',
    'No known family disease was reported, so no additional family-history follow-up is suggested by this input alone.': 'သိရှိထားသော မိသားစုရောဂါ မရှိကြောင်း မှတ်တမ်းတင်ထားသဖြင့် ဤ input တစ်ခုတည်းအရ ထပ်မံနောက်ဆက်တွဲစစ်ဆေးရန် မလိုအပ်ပါ။',
    'Family disease history is unknown, so this part of the assessment is less certain.': 'မိသားစုရောဂါရာဇဝင်ကို မသိရှိသဖြင့် အကဲဖြတ်မှု၏ ဤအပိုင်းတွင် မသေချာမှု ပိုများသည်။',
    'Immediate Condition': 'ချက်ချင်းအခြေအနေ',
    'Birth-Related': 'မွေးဖွားမှုဆိုင်ရာ',
    'Family History': 'မိသားစုရာဇဝင်'
  });

  const translatedAttributes = ['placeholder', 'title', 'aria-label'];
  const ignoredParents = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'CODE', 'PRE']);
  const embeddedPhrases = [
    'Heartbeat or breathing concern. Assess immediately.',
    'Blue/pale colour, absent reflex, or limp tone. Assess immediately.',
    'Reduced reflex or tone. Reassess clinically.',
    'Critical total. Assess immediately; do not delay care.',
    'APGAR below 7. Record the next 5-minute observation. Do not delay care.',
    'Weak or irregular breathing',
    'No heartbeat detected',
    'Heart rate below 100 bpm',
    'No breathing detected',
    'No reflex response to stimulation',
    'Limited reflex response (grimace only)',
    'Limp or absent muscle tone',
    'Reduced muscle tone (some flexion)',
    'Have the neonatal clinician reassess this component and document the finding.',
    'Prematurity and maternal medication can affect tone and reflex responses; this notice does not diagnose a condition or prescribe treatment.',
    'Seek immediate in-person clinical assessment if this describes the baby now. Do not wait for an APGAR total.',
    'Model trained on 2024 U.S. records and evaluated unchanged on 2023 records.'
  ];

  function translatedText(value) {
    const trimmed = value.trim();
    if (translations[trimmed]) return translations[trimmed];
    let match = trimmed.match(/^Birth Summary of (.+)$/);
    if (match) return 'မွေးဖွားမှု အကျဉ်းချုပ် — ' + match[1];
    match = trimmed.match(/^Module (\d+)$/);
    if (match) return 'ကဏ္ဍ ' + match[1];
    match = trimmed.match(/^(Immediate condition|Birth-related monitoring|Family-history follow-up) · (Low|Moderate|High|Unknown)$/);
    if (match) return translations[match[1]] + ' · ' + translations[match[2]];
    match = trimmed.match(/^(\d+) family condition was reported; at least one affects both parents, so follow-up may need additional attention\.$/);
    if (match) return 'မိသားစုရောဂါ ' + match[1] + ' ခု မှတ်တမ်းတင်ထားပြီး အနည်းဆုံးတစ်ခုသည် မိဘနှစ်ဦးလုံးတွင် ရှိသောကြောင့် နောက်ဆက်တွဲစစ်ဆေးမှု ပိုမိုလိုအပ်နိုင်သည်။';
    match = trimmed.match(/^(\d+) family condition was reported; at least one affects a parent, so follow-up may need additional attention\.$/);
    if (match) return 'မိသားစုရောဂါ ' + match[1] + ' ခု မှတ်တမ်းတင်ထားပြီး အနည်းဆုံးတစ်ခုသည် မိဘတစ်ဦးတွင် ရှိသောကြောင့် နောက်ဆက်တွဲစစ်ဆေးမှု ပိုမိုလိုအပ်နိုင်သည်။';
    match = trimmed.match(/^(\d+) family conditions were reported; at least one affects both parents, so follow-up may need additional attention\.$/);
    if (match) return 'မိသားစုရောဂါ ' + match[1] + ' ခု မှတ်တမ်းတင်ထားပြီး အနည်းဆုံးတစ်ခုသည် မိဘနှစ်ဦးလုံးတွင် ရှိသောကြောင့် နောက်ဆက်တွဲစစ်ဆေးမှု ပိုမိုလိုအပ်နိုင်သည်။';
    match = trimmed.match(/^(\d+) family conditions were reported; at least one affects a parent, so follow-up may need additional attention\.$/);
    if (match) return 'မိသားစုရောဂါ ' + match[1] + ' ခု မှတ်တမ်းတင်ထားပြီး အနည်းဆုံးတစ်ခုသည် မိဘတစ်ဦးတွင် ရှိသောကြောင့် နောက်ဆက်တွဲစစ်ဆေးမှု ပိုမိုလိုအပ်နိုင်သည်။';
    match = trimmed.match(/^(\d+) family (?:condition was|conditions were) reported in another family member\.$/);
    if (match) return 'အခြားမိသားစုဝင်တွင် မိသားစုရောဂါ ' + match[1] + ' ခု ရှိကြောင်း မှတ်တမ်းတင်ထားသည်။';
    match = trimmed.match(/^(\d+) family (?:condition was|conditions were) reported, but at least one affected relative is unknown\.$/);
    if (match) return 'မိသားစုရောဂါ ' + match[1] + ' ခု မှတ်တမ်းတင်ထားသော်လည်း ရောဂါရှိသော ဆွေမျိုး အနည်းဆုံးတစ်ဦးကို မသိရှိပါ။';
    match = trimmed.match(/^(\d+)-minute observation$/);
    if (match) return match[1] + ' မိနစ် စောင့်ကြည့်ချက်';
    match = trimmed.match(/^(\d+)-minute APGAR$/);
    if (match) return match[1] + ' မိနစ် APGAR';
    match = trimmed.match(/^([\d.]+) weeks$/);
    if (match) return match[1] + ' ပတ်';
    match = trimmed.match(/^([\d.]+) lb$/);
    if (match) return match[1] + ' ပေါင် (lb)';
    match = trimmed.match(/^([\d.]+) kg$/);
    if (match) return match[1] + ' ကီလိုဂရမ် (kg)';
    match = trimmed.match(/^([\d.]+) g$/);
    if (match) return match[1] + ' ဂရမ် (g)';
    match = trimmed.match(/^Recorded total: (\d+)\/10\.$/);
    if (match) return 'မှတ်တမ်းတင်ထားသော စုစုပေါင်းအမှတ်: ' + match[1] + '/10။';
    match = trimmed.match(/^Low total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် နိမ့်သည် — ' + match[1] + '/10';
    match = trimmed.match(/^Moderately abnormal total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် အတန်အသင့် မူမမှန်ပါ — ' + match[1] + '/10';
    match = trimmed.match(/^Reassuring total — (\d+)\/10$/);
    if (match) return 'စုစုပေါင်းအမှတ် စိတ်ချရသည် — ' + match[1] + '/10';
    match = trimmed.match(/^Birth Information\s*(→)?$/);
    if (match) return translations['Birth Information'] + (match[1] ? ' →' : '');
    match = trimmed.match(/^Family History\s*(→)?$/);
    if (match) return translations['Family History'] + (match[1] ? ' →' : '');
    match = trimmed.match(/^Review\s*(→)?$/);
    if (match) return translations.Review + (match[1] ? ' →' : '');
    match = trimmed.match(/^(←\s*)?Edit$/);
    if (match) return (match[1] || '') + translations.Edit;
    match = trimmed.match(/^(←\s*)?Back$/);
    if (match) return (match[1] || '') + translations.Back;
    match = trimmed.match(/^(←\s*)?Back to Review & Edit$/);
    if (match) return (match[1] || '') + translations['Back to Review & Edit'];
    match = trimmed.match(/^\+ 5 minutes — add (\d+)-minute observation$/);
    if (match) return '+ ၅ မိနစ် — ' + match[1] + ' မိနစ် စောင့်ကြည့်ချက် ထည့်ရန်';
    match = trimmed.match(/^Maximum (\d+) diseases added$/);
    if (match) return 'ရောဂါအများဆုံး ' + match[1] + ' ခု ထည့်ပြီးပါပြီ';
    match = trimmed.match(/^Yes — (.+)$/);
    if (match) return translations.Yes + ' — ' + match[1].split(';').map(function (item) { return translatedText(item.trim()); }).join('; ');
    if (trimmed.includes(';') && trimmed.split(';').every(function (item) { return / — (Father|Mother|Both parents|Other family member|Unknown)$/.test(item.trim()); })) {
      return trimmed.split(';').map(function (item) { return translatedText(item.trim()); }).join('; ');
    }
    match = trimmed.match(/^(.+) — (Father|Mother|Both parents|Other family member|Unknown)$/);
    if (match) return translatedText(match[1]) + ' — ' + translations[match[2]];
    match = trimmed.match(/^APGAR below 7\. Record the (\d+)-minute observation\. Do not delay care\.$/);
    if (match) return 'APGAR ၇ အောက်ဖြစ်သည်။ ' + match[1] + ' မိနစ် စောင့်ကြည့်ချက်ကို မှတ်တမ်းတင်ပါ။ ကုသမှု မနှောင့်နှေးပါနှင့်။';
    match = trimmed.match(/^(\d+) minutes: APGAR (\d+\/10); support\/resuscitation: (.+)\.$/);
    if (match) return match[1] + ' မိနစ်: APGAR ' + match[2] + '; အသက်ကယ်အကူအညီ: ' + (translations[match[3][0].toUpperCase() + match[3].slice(1)] || match[3]) + '။';
    match = trimmed.match(/^Not available: 1-minute observation not recorded\. Inference uses the latest complete (\d+)-minute observation, without averaging scores\.$/);
    if (match) return '၁ မိနစ် စောင့်ကြည့်ချက် မမှတ်တမ်းတင်ထားသဖြင့် မရရှိနိုင်ပါ။ အမှတ်များကို ပျမ်းမျှမယူဘဲ နောက်ဆုံးပြည့်စုံသော ' + match[1] + ' မိနစ် စောင့်ကြည့်ချက်ကို inference အတွက် အသုံးပြုပါသည်။';
    match = trimmed.match(/^Final immediate-condition index: ([\d.]+)\/100 \((.+)\)\. Action priority: (.+)\.$/);
    if (match) return 'နောက်ဆုံး ချက်ချင်းအခြေအနေညွှန်းကိန်း: ' + match[1] + '/100 (' + (translations[match[2]] || match[2]) + ')။ လုပ်ဆောင်ရန် ဦးစားပေးအဆင့်: ' + (translations[match[3]] || match[3]) + '။';
    match = trimmed.match(/^Graph interpretation: curves show fuzzy rule activation; the vertical line marks the ([\d.]+)\/100 index\. This index is not a probability\.( Component alerts also guide clinical action\.)?$/);
    if (match) return 'Graph ရှင်းလင်းချက်: မျဉ်းကွေးများသည် fuzzy rule activation ကို ပြပြီး ဒေါင်လိုက်မျဉ်းသည် ' + match[1] + '/100 ညွှန်းကိန်းကို ဖော်ပြသည်။ ဤညွှန်းကိန်းသည် ဖြစ်နိုင်ခြေ မဟုတ်ပါ။' + (match[2] ? ' အချက်တစ်ခုချင်း သတိပေးချက်များကလည်း ဆေးဘက်လုပ်ဆောင်မှုကို လမ်းညွှန်ပါသည်။' : '');
    match = trimmed.match(/^No heartbeat\/breathing safety override\. The immediate index comes from APGAR (\d+\/10) and (a reported|no reported) delivery complication; component notices can separately change the action priority\.$/);
    if (match) return 'နှလုံးခုန်ခြင်း/အသက်ရှူခြင်း ဘေးကင်းရေး override မရှိပါ။ ချက်ချင်းအခြေအနေညွှန်းကိန်းသည် APGAR ' + match[1] + ' နှင့် ' + (match[2] === 'a reported' ? 'မှတ်တမ်းတင်ထားသော မွေးဖွားမှု ပြဿနာ' : 'မွေးဖွားမှု ပြဿနာမရှိကြောင်း မှတ်တမ်း') + 'မှ တွက်ချက်ထားသည်။ အချက်တစ်ခုချင်း သတိပေးချက်များက လုပ်ဆောင်ရန် ဦးစားပေးအဆင့်ကို သီးခြားပြောင်းလဲနိုင်သည်။';
    match = trimmed.match(/^Reference: latest complete (\d+)-minute observation\.$/);
    if (match) return 'ရည်ညွှန်းချက်: နောက်ဆုံးပြည့်စုံသော ' + match[1] + ' မိနစ် စောင့်ကြည့်ချက်။';
    match = trimmed.match(/^Reason for High: component safety override — (.+)\. The APGAR total alone did not set High; this numeric override is a conservative project policy, not a guideline-defined probability\.$/);
    if (match) return 'High ဖြစ်ရသည့်အကြောင်းရင်း: အချက်တစ်ခုချင်း ဘေးကင်းရေး override — ' + translatedText(match[1]) + '။ APGAR စုစုပေါင်းအမှတ်တစ်ခုတည်းကြောင့် High ဖြစ်ခြင်းမဟုတ်ပါ။ ဤကိန်းဂဏန်း override သည် project ၏ သတိထားသည့် policy ဖြစ်ပြီး guideline မှ သတ်မှတ်ထားသော ဖြစ်နိုင်ခြေ မဟုတ်ပါ။';
    match = trimmed.match(/^(Respiration|Pulse|Appearance|Grimace|Activity) (\d)\/2: (.+)$/);
    if (match) return (translations[match[1]] || match[1]) + ' ' + match[2] + '/2: ' + translatedText(match[3]);
    match = trimmed.match(/^The 5-minute APGAR total was below 7\. Record a fresh observation at (\d+) minutes after birth, and further scoring up to 20 minutes as clinically indicated\. Do not delay clinical care\.$/);
    if (match) return '၅ မိနစ် APGAR စုစုပေါင်းအမှတ်သည် ၇ အောက်ဖြစ်သည်။ မွေးဖွားပြီး ' + match[1] + ' မိနစ်တွင် အသစ်ပြန်လည်စောင့်ကြည့်မှတ်တမ်းတင်ပြီး ဆေးဘက်လိုအပ်ချက်အရ မိနစ် ၂၀ အထိ ဆက်လက်အမှတ်ပေးပါ။ ကုသမှု မနှောင့်နှေးပါနှင့်။';
    match = trimmed.match(/^Gestational age: ([\d.]+) weeks \((.+)\)\.$/);
    if (match) return 'ကိုယ်ဝန်သက်တမ်း: ' + match[1] + ' ပတ် (' + (translations[match[2][0].toUpperCase() + match[2].slice(1)] || match[2]) + ')။';
    match = trimmed.match(/^Birth weight: ([\d.]+) g \((.+)\)\.$/);
    if (match) return 'မွေးဖွားချိန် ကိုယ်အလေးချိန်: ' + match[1] + ' g (' + (translations[match[2][0].toUpperCase() + match[2].slice(1)] || match[2]) + ')။';
    match = trimmed.match(/^Maternal age: ([\d.]+) years; contextual input only\.$/);
    if (match) return 'မိခင်အသက်: ' + match[1] + ' နှစ်; ဆက်စပ်အချက်အလက်အဖြစ်သာ အသုံးပြုသည်။';
    match = trimmed.match(/^Delivery complication: (Reported|Not reported)\.$/);
    if (match) return 'မွေးဖွားမှု ပြဿနာ: ' + translations[match[1]] + '။';
    match = trimmed.match(/^Birth-monitoring index: ([\d.]+)\/100\.$/);
    if (match) return 'မွေးဖွားမှု စောင့်ကြည့်ညွှန်းကိန်း: ' + match[1] + '/100။';
    match = trimmed.match(/^Final monitoring level: (.+)\.$/);
    if (match) return 'နောက်ဆုံး စောင့်ကြည့်အဆင့်: ' + (translations[match[1]] || match[1]) + '။';
    match = trimmed.match(/^Monitoring priority: (.+)\.$/);
    if (match) return 'စောင့်ကြည့်ရန် ဦးစားပေးအဆင့်: ' + (translations[match[1]] || match[1]) + '။';
    match = trimmed.match(/^(.+): (Low|Moderate|High) rule activation ([\d.]+)\.$/);
    if (match) return (translations[match[1]] || match[1]) + ': ' + translations[match[2]] + ' rule activation ' + match[3] + '။';
    match = trimmed.match(/^Combined fuzzy output: centre-of-area index ([\d.]+); final label (Low|Moderate|High) \(Low below 30, Moderate 30 to below 70, High 70 or above\)\.$/);
    if (match) return 'ပေါင်းစပ် fuzzy output: centre-of-area index ' + match[1] + '; နောက်ဆုံးအဆင့် ' + translations[match[2]] + ' (Low 30 အောက်၊ Moderate 30 မှ 70 အောက်၊ High 70 နှင့်အထက်)။';
    match = trimmed.match(/^Preterm birth \(([\d.]+) weeks\): assess feeding, temperature stability and respiratory status\.$/);
    if (match) return 'လမစေ့မွေးဖွားမှု (' + match[1] + ' ပတ်): နို့တိုက်ကျွေးမှု၊ ကိုယ်အပူချိန်တည်ငြိမ်မှုနှင့် အသက်ရှူမှုအခြေအနေကို စစ်ဆေးပါ။';
    match = trimmed.match(/^(\d+) completed weeks$/);
    if (match) return 'ပြီးပြည့်စုံသော ' + match[1] + ' ပတ်';
    match = trimmed.match(/^(\d+) years$/);
    if (match) return match[1] + ' နှစ်';
    match = trimmed.match(/^Historical 2023 evaluation: (\d+) records\.$/);
    if (match) return '2023 ယခင်ဒေတာ အကဲဖြတ်မှု: မှတ်တမ်း ' + match[1] + ' ခု။';
    let phraseTranslated = trimmed;
    embeddedPhrases.forEach(function (phrase) {
      phraseTranslated = phraseTranslated.split(phrase).join(translations[phrase]);
    });
    if (phraseTranslated !== trimmed) return phraseTranslated;
    return trimmed;
  }

  window.NHRA_TRANSLATE_TEXT = translatedText;

  function translateTextNode(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return;
    if (node.parentElement && (ignoredParents.has(node.parentElement.tagName) || node.parentElement.isContentEditable)) return;
    const original = node.nodeValue;
    const previous = originalText.get(node);
    if (!previous || original !== previous.translated) {
      originalText.set(node, { english: original, translated: null });
    }
    const trimmed = original.trim();
    if (node.parentElement && node.parentElement.childNodes.length === 1 && !node.parentElement.dataset.i18nEnglish) {
      node.parentElement.dataset.i18nEnglish = trimmed;
    }
    const translated = translatedText(trimmed);
    if (translated === trimmed) return;
    const translatedValue = original.replace(trimmed, translated);
    originalText.set(node, { english: original, translated: translatedValue });
    node.nodeValue = translatedValue;
  }

  function translateAttributes(element) {
    translatedAttributes.forEach(function (attribute) {
      if (!element.hasAttribute(attribute)) return;
      const value = element.getAttribute(attribute);
      const translated = translatedText(value);
      if (translated === value.trim()) return;
      const saved = originalAttributes.get(element) || {};
      saved[attribute] = { english: value, translated: translated };
      originalAttributes.set(element, saved);
      element.setAttribute(attribute, translated);
    });
  }

  function translateElement(element) {
    if (!(element instanceof Element)) return;
    translateAttributes(element);
    element.querySelectorAll('*').forEach(translateAttributes);
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) translateTextNode(node);
  }

  function restoreEnglish(element) {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const saved = originalText.get(node);
      if (saved && node.nodeValue === saved.translated) node.nodeValue = saved.english;
    }
    [element].concat(Array.from(element.querySelectorAll('*'))).forEach(function (child) {
      const attributes = originalAttributes.get(child);
      if (!attributes) return;
      Object.entries(attributes).forEach(function ([name, saved]) {
        if (child.getAttribute(name) === saved.translated) child.setAttribute(name, saved.english);
      });
    });
  }

  function applyLanguage(language) {
    activeLanguage = language === 'my' ? 'my' : 'en';
    window.NHRA_LANGUAGE = activeLanguage;
    document.documentElement.lang = activeLanguage;
    if (activeLanguage === 'my') translateElement(document.documentElement);
    else restoreEnglish(document.documentElement);
  }

  window.NHRA_SET_LANGUAGE = applyLanguage;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { applyLanguage(activeLanguage); }, { once: true });
  } else {
    applyLanguage(activeLanguage);
  }

  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (activeLanguage !== 'my') return;
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
