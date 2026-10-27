import random
import requests
import streamlit as st
from collections import Counter

# =========================================================
# 바이오 헌터
# =========================================================

st.set_page_config(
    page_title="바이오 헌터",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- 디자인 --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f4f8ed 0%, #fffdf6 100%);
}
h1, h2, h3 {
    color: #285943;
}
.hero {
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(120deg, #d9edc8, #fff0c7);
    margin-bottom: 18px;
}
.hero h1 {
    font-size: 42px;
    margin-bottom: 8px;
}
.hero p {
    font-size: 17px;
    color: #365444;
}
.info-card {
    padding: 16px;
    background: #ffffff;
    border: 1px solid #dce8d3;
    border-radius: 16px;
    margin-bottom: 12px;
}
.small-note {
    color: #647568;
    font-size: 13px;
}
div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 생물 데이터
# 각 항목: 한국어 이름, 영문명, 학명, 분류, 서식지,
# 먹이, 특징, 생물학 정보, 희귀도, 위키백과 문서명
# =========================================================

RAW_SPECIES = [
    # 곤충
    ("호랑나비", "Asian Swallowtail", "Papilio xuthus", "곤충", "정원,초원,숲", "식물의 꿀", "노란색과 검은색 무늬의 날개가 특징이다.", "애벌레는 운향과 식물을 먹는다.", "일반", "Papilio_xuthus"),
    ("배추흰나비", "Small White", "Pieris rapae", "곤충", "정원,초원", "식물의 꿀", "흰 날개에 검은 점이 있다.", "애벌레는 배추와 같은 십자화과 식물을 먹는다.", "일반", "Pieris_rapae"),
    ("모시나비", "Clouded Apollo", "Parnassius mnemosyne", "곤충", "산,초원", "식물의 꿀", "반투명한 흰 날개를 가진 나비이다.", "일부 종은 서식지 환경 변화에 민감하다.", "희귀", "Parnassius_mnemosyne"),
    ("꿀벌", "Western Honey Bee", "Apis mellifera", "곤충", "정원,초원,숲", "꽃꿀과 꽃가루", "여러 마리가 역할을 나누어 생활한다.", "꽃가루받이를 돕는 중요한 곤충이다.", "일반", "Western_honey_bee"),
    ("뒤영벌", "Bumblebee", "Bombus", "곤충", "초원,정원,산", "꽃꿀과 꽃가루", "털이 많고 몸집이 통통하다.", "몸을 진동시켜 꽃가루를 털어내는 종도 있다.", "희귀", "Bumblebee"),
    ("무당벌레", "Ladybird", "Coccinellidae", "곤충", "정원,초원,숲", "진딧물 등", "둥근 몸과 점무늬가 특징이다.", "진딧물을 먹어 농작물 보호에 도움을 주기도 한다.", "일반", "Coccinellidae"),
    ("잠자리", "Dragonfly", "Anisoptera", "곤충", "연못,습지,초원", "작은 곤충", "큰 눈과 두 쌍의 날개를 가진다.", "애벌레는 물속에서 생활한다.", "일반", "Dragonfly"),
    ("왕잠자리", "Common Green Darner", "Anax junius", "곤충", "연못,습지", "작은 곤충", "비행 능력이 뛰어난 잠자리이다.", "일부 개체는 먼 거리를 이동한다.", "희귀", "Anax_junius"),
    ("사마귀", "Praying Mantis", "Mantodea", "곤충", "초원,정원,숲", "곤충 등", "앞다리로 먹이를 붙잡는다.", "주변 환경에 맞추어 몸색이 달라 보이기도 한다.", "일반", "Mantis"),
    ("장수풍뎅이", "Japanese Rhinoceros Beetle", "Trypoxylus dichotomus", "곤충", "숲", "수액과 과일", "수컷은 큰 뿔을 가진다.", "수컷끼리 뿔을 이용해 경쟁하기도 한다.", "희귀", "Trypoxylus_dichotomus"),
    ("사슴벌레", "Stag Beetle", "Lucanus", "곤충", "숲", "수액과 과일", "큰 턱이 특징이다.", "애벌레는 썩은 나무에서 자라는 경우가 많다.", "희귀", "Stag_beetle"),
    ("반딧불이", "Firefly", "Lampyridae", "곤충", "습지,숲", "작은 동물 등", "배 부분에서 빛을 낸다.", "빛을 이용해 짝을 찾는 신호를 보내기도 한다.", "초희귀", "Firefly"),
    ("매미", "Cicada", "Cicadidae", "곤충", "숲,정원", "식물 수액", "수컷은 큰 울음소리를 낸다.", "애벌레는 땅속에서 오랜 기간 자라기도 한다.", "일반", "Cicada"),
    ("개미", "Ant", "Formicidae", "곤충", "정원,숲,초원", "식물과 작은 동물 등", "무리 생활을 하는 사회성 곤충이다.", "여왕개미와 일개미 등이 역할을 나누는 종이 많다.", "일반", "Ant"),
    ("귀뚜라미", "Cricket", "Gryllidae", "곤충", "초원,정원", "식물과 작은 동물", "수컷은 날개를 비벼 소리를 낸다.", "더듬이로 주변 환경을 감지한다.", "일반", "Cricket"),
    ("메뚜기", "Grasshopper", "Caelifera", "곤충", "초원,정원", "식물", "뒷다리가 발달해 멀리 뛸 수 있다.", "식물의 잎을 먹는 초식성 곤충이다.", "일반", "Grasshopper"),
    ("물방개", "Predaceous Diving Beetle", "Dytiscidae", "곤충", "연못,습지", "작은 수생동물", "물속에서 헤엄치는 딱정벌레이다.", "공기 방울을 이용해 물속에서 호흡을 이어 간다.", "희귀", "Dytiscidae"),
    ("소금쟁이", "Water Strider", "Gerridae", "곤충", "연못,습지", "작은 곤충", "물 표면 위를 걸어 다닌다.", "다리와 물 표면의 장력을 이용한다.", "일반", "Gerridae"),
    ("흰개미", "Termite", "Isoptera", "곤충", "숲", "나무 속 섬유질", "무리를 이루어 생활한다.", "장내 미생물의 도움을 받아 목재 성분을 분해한다.", "희귀", "Termite"),
    ("왕개미", "Carpenter Ant", "Camponotus", "곤충", "숲,정원", "곤충과 당분", "큰 몸집을 가진 개미 무리이다.", "나무에 둥지를 만드는 종도 있다.", "희귀", "Carpenter_ant"),

    # 포유류
    ("붉은여우", "Red Fox", "Vulpes vulpes", "포유류", "숲,초원,산", "작은 동물과 열매", "뾰족한 귀와 긴 꼬리가 특징이다.", "환경에 따라 다양한 먹이를 이용한다.", "희귀", "Red_fox"),
    ("고라니", "Water Deer", "Hydropotes inermis", "포유류", "습지,초원,숲", "식물", "수컷은 작은 송곳니가 발달한다.", "한국에서 볼 수 있는 사슴과 동물이다.", "희귀", "Water_deer"),
    ("노루", "Siberian Roe Deer", "Capreolus pygargus", "포유류", "숲,산", "풀과 나뭇잎", "몸집이 비교적 작고 민첩하다.", "주로 식물을 먹는 초식동물이다.", "희귀", "Siberian_roe_deer"),
    ("멧돼지", "Wild Boar", "Sus scrofa", "포유류", "숲,산", "뿌리와 열매,작은 동물", "주둥이와 강한 몸이 특징이다.", "먹이 종류가 다양한 잡식동물이다.", "일반", "Wild_boar"),
    ("다람쥐", "Siberian Chipmunk", "Eutamias sibiricus", "포유류", "숲,산", "씨앗과 열매", "등에 줄무늬가 있다.", "먹이를 볼주머니에 넣어 옮기기도 한다.", "일반", "Siberian_chipmunk"),
    ("청설모", "Pallas's Squirrel", "Callosciurus erythraeus", "포유류", "숲,산,정원", "씨앗과 열매", "긴 꼬리와 민첩한 움직임이 특징이다.", "나무 위에서 생활하는 시간이 많다.", "일반", "Pallas's_squirrel"),
    ("고슴도치", "Hedgehog", "Erinaceinae", "포유류", "숲,초원,정원", "곤충과 작은 동물", "등에 뾰족한 가시가 있다.", "위협을 느끼면 몸을 둥글게 말기도 한다.", "희귀", "Hedgehog"),
    ("수달", "Eurasian Otter", "Lutra lutra", "포유류", "강,습지,연못", "물고기와 수생동물", "물속 생활에 적응한 몸을 가졌다.", "깨끗한 수생 환경을 유지하는 것이 중요하다.", "초희귀", "Eurasian_otter"),
    ("너구리", "Raccoon Dog", "Nyctereutes procyonoides", "포유류", "숲,습지", "열매와 작은 동물", "얼굴에 어두운 무늬가 있다.", "개과에 속하며 너구리와 라쿤은 다른 동물이다.", "일반", "Raccoon_dog"),
    ("반달가슴곰", "Asiatic Black Bear", "Ursus thibetanus", "포유류", "숲,산", "열매와 곤충 등", "가슴에 밝은색 초승달 모양 무늬가 나타난다.", "서식지 보전이 중요한 야생동물이다.", "초희귀", "Asian_black_bear"),
    ("고래", "Whale", "Cetacea", "포유류", "바다", "물고기 또는 작은 갑각류", "물속에서 생활하는 포유류이다.", "공기로 호흡하고 새끼에게 젖을 먹인다.", "초희귀", "Whale"),
    ("돌고래", "Dolphin", "Delphinidae", "포유류", "바다", "물고기와 오징어", "소리와 반향을 이용해 주변을 파악한다.", "무리 생활을 하는 종이 많다.", "희귀", "Dolphin"),
    ("박쥐", "Bat", "Chiroptera", "포유류", "숲,산", "곤충 또는 과일", "날 수 있는 유일한 포유류 무리이다.", "많은 종이 초음파를 이용해 주변을 감지한다.", "희귀", "Bat"),
    ("두더지", "Mole", "Talpidae", "포유류", "초원,정원,숲", "지렁이와 곤충", "땅속 생활에 적응한 앞발을 가졌다.", "흙 속에서 먹이를 찾는다.", "일반", "Mole"),
    ("고양이", "Domestic Cat", "Felis catus", "포유류", "정원,숲", "육류", "뛰어난 청각과 야간 시력이 특징이다.", "사람과 함께 살아온 가축화된 동물이다.", "일반", "Cat"),
    ("개", "Domestic Dog", "Canis lupus familiaris", "포유류", "정원,초원", "육류 등", "후각이 발달했다.", "사람과 오랜 기간 함께 살아온 동물이다.", "일반", "Dog"),

    # 조류
    ("까치", "Oriental Magpie", "Pica serica", "조류", "정원,숲,초원", "곤충과 열매 등", "검은색과 흰색 깃털이 특징이다.", "다양한 먹이를 먹는 잡식성 조류이다.", "일반", "Oriental_magpie"),
    ("참새", "Eurasian Tree Sparrow", "Passer montanus", "조류", "정원,초원", "씨앗과 곤충", "작은 몸집과 갈색 깃털이 특징이다.", "사람이 사는 주변에서도 흔히 볼 수 있다.", "일반", "Eurasian_tree_sparrow"),
    ("까마귀", "Carrion Crow", "Corvus corone", "조류", "숲,산,정원", "곤충과 열매 등", "검은 깃털과 높은 학습 능력이 특징이다.", "도구를 사용하거나 문제를 해결하는 행동이 관찰된다.", "일반", "Carrion_crow"),
    ("수리부엉이", "Eurasian Eagle-Owl", "Bubo bubo", "조류", "산,숲", "작은 포유류와 새", "큰 몸집과 귀깃이 특징이다.", "야간에 활동하는 맹금류이다.", "초희귀", "Eurasian_eagle-owl"),
    ("흰뺨검둥오리", "Eastern Spot-billed Duck", "Anas zonorhyncha", "조류", "연못,습지", "수생식물과 작은 동물", "부리 끝의 노란색 무늬가 특징이다.", "물가에서 먹이를 찾는다.", "일반", "Eastern_spot-billed_duck"),
    ("물총새", "Common Kingfisher", "Alcedo atthis", "조류", "연못,습지", "물고기", "푸른색과 주황색 깃털이 눈에 띈다.", "물속으로 뛰어들어 물고기를 잡는다.", "희귀", "Common_kingfisher"),
    ("황조롱이", "Common Kestrel", "Falco tinnunculus", "조류", "초원,산", "곤충과 작은 동물", "공중에서 정지 비행하듯 먹이를 살핀다.", "시각을 이용해 먹이를 찾아낸다.", "희귀", "Common_kestrel"),
    ("흰꼬리수리", "White-tailed Eagle", "Haliaeetus albicilla", "조류", "바다,습지", "물고기와 새", "넓은 날개와 흰 꼬리가 특징이다.", "물가 주변에서 먹이를 찾는 대형 맹금류이다.", "초희귀", "White-tailed_eagle"),
    ("제비", "Barn Swallow", "Hirundo rustica", "조류", "초원,정원", "날아다니는 곤충", "길게 갈라진 꼬리가 특징이다.", "비행하면서 곤충을 잡아먹는다.", "일반", "Barn_swallow"),
    ("두루미", "Red-crowned Crane", "Grus japonensis", "조류", "습지,초원", "식물과 작은 동물", "머리 위 붉은 피부가 특징이다.", "습지와 논 등에서 먹이를 찾는다.", "초희귀", "Red-crowned_crane"),
    ("펭귄", "Penguin", "Spheniscidae", "조류", "바다", "물고기와 갑각류", "날개가 헤엄치기에 적합하게 변했다.", "날지 못하지만 물속에서 빠르게 움직인다.", "희귀", "Penguin"),
    ("타조", "Ostrich", "Struthio camelus", "조류", "초원", "식물과 작은 동물", "현존하는 가장 큰 새이다.", "강한 다리로 빠르게 달릴 수 있다.", "희귀", "Ostrich"),

    # 양서류와 파충류
    ("청개구리", "Japanese Tree Frog", "Dryophytes japonicus", "양서류", "정원,습지,연못", "곤충", "발가락 끝에 흡착 구조가 있다.", "피부가 촉촉하게 유지되어야 한다.", "일반", "Dryophytes_japonicus"),
    ("참개구리", "East Asian Brown Frog", "Pelophylax nigromaculatus", "양서류", "연못,습지", "곤충과 작은 동물", "물가에서 흔히 관찰되는 개구리이다.", "올챙이 시기에는 아가미로 호흡한다.", "일반", "Pelophylax_nigromaculatus"),
    ("두꺼비", "Asian Common Toad", "Bufo gargarizans", "양서류", "숲,정원,습지", "곤충과 지렁이", "피부가 울퉁불퉁하다.", "피부샘에서 방어 물질을 분비할 수 있다.", "희귀", "Bufo_gargarizans"),
    ("도롱뇽", "Korean Salamander", "Hynobius leechii", "양서류", "숲,산,습지", "작은 무척추동물", "도마뱀과 비슷해 보이지만 양서류이다.", "성체가 된 뒤에도 습한 환경을 선호한다.", "희귀", "Hynobius_leechii"),
    ("바다거북", "Green Sea Turtle", "Chelonia mydas", "파충류", "바다", "해초와 해조류 등", "바다에 적응한 거북이다.", "알을 낳을 때 육지로 올라온다.", "초희귀", "Green_sea_turtle"),
    ("자라", "Chinese Softshell Turtle", "Pelodiscus sinensis", "파충류", "연못,습지", "물고기와 작은 동물", "딱딱한 등딱지 대신 부드러운 피부가 덮여 있다.", "물속 생활에 적응한 거북류이다.", "희귀", "Chinese_softshell_turtle"),
    ("살모사", "Asian Pit Viper", "Gloydius brevicaudus", "파충류", "산,숲", "작은 포유류와 개구리", "독을 가진 뱀이다.", "야생 뱀은 발견해도 가까이 가지 않아야 한다.", "초희귀", "Gloydius_brevicaudus"),
    ("도마뱀", "Lizard", "Lacertilia", "파충류", "초원,숲,산", "곤충과 작은 동물", "비늘로 덮인 피부를 가진다.", "일부 종은 꼬리를 잘라 포식자를 피한다.", "희귀", "Lizard"),

    # 물고기와 바다 생물
    ("잉어", "Common Carp", "Cyprinus carpio", "물고기", "연못,습지", "수생식물과 작은 동물", "입 주변에 짧은 수염이 있다.", "먹이를 찾기 위해 바닥을 뒤지기도 한다.", "일반", "Common_carp"),
    ("금붕어", "Goldfish", "Carassius auratus", "물고기", "연못", "사료와 수생생물", "다양한 색과 지느러미 모양을 가진다.", "사람이 관상용으로 기르도록 개량한 물고기이다.", "일반", "Goldfish"),
    ("송어", "Trout", "Salmo trutta", "물고기", "강,산", "수생곤충과 작은 물고기", "차고 산소가 풍부한 물에서 사는 종이 많다.", "수온과 수질 변화에 영향을 받는다.", "희귀", "Trout"),
    ("연어", "Salmon", "Salmo salar", "물고기", "강,바다", "작은 물고기와 갑각류", "일부 종은 바다와 강을 오간다.", "번식을 위해 태어난 강으로 돌아오는 종이 있다.", "희귀", "Salmon"),
    ("흰동가리", "Clownfish", "Amphiprioninae", "물고기", "바다", "작은 동물과 조류", "주황색과 흰색 줄무늬가 흔하다.", "말미잘과 공생 관계를 맺는 종이 있다.", "희귀", "Amphiprioninae"),
    ("해마", "Seahorse", "Hippocampus", "물고기", "바다", "작은 갑각류", "말처럼 생긴 머리와 감는 꼬리가 특징이다.", "수컷이 알을 품는 육아낭을 가진다.", "초희귀", "Seahorse"),
    ("문어", "Common Octopus", "Octopus vulgaris", "무척추동물", "바다", "게와 조개 등", "여덟 개의 팔을 가진다.", "위장과 문제 해결 능력이 잘 알려져 있다.", "희귀", "Octopus"),
    ("오징어", "Squid", "Teuthida", "무척추동물", "바다", "물고기와 갑각류", "물줄기를 뿜어 빠르게 이동한다.", "몸색을 바꾸어 의사소통하거나 숨는 종이 있다.", "일반", "Squid"),
    ("불가사리", "Starfish", "Asteroidea", "무척추동물", "바다", "조개 등", "팔이 여러 개 뻗은 별 모양이다.", "일부 종은 손상된 팔을 재생할 수 있다.", "희귀", "Starfish"),
    ("해파리", "Jellyfish", "Scyphozoa", "무척추동물", "바다", "플랑크톤과 작은 동물", "젤리처럼 부드러운 몸을 가진다.", "촉수의 자포로 먹이를 잡는 종이 있다.", "희귀", "Jellyfish"),
    ("산호", "Coral", "Anthozoa", "무척추동물", "바다", "플랑크톤 등", "작은 산호충이 모여 군체를 이루기도 한다.", "산호초는 다양한 해양 생물의 서식처이다.", "초희귀", "Coral"),
    ("대왕조개", "Giant Clam", "Tridacna gigas", "무척추동물", "바다", "공생 조류가 만든 영양분 등", "매우 큰 껍데기를 가진 조개이다.", "조직 속 공생 조류로부터 영양을 얻는다.", "초희귀", "Tridacna_gigas"),
    ("갯지렁이", "Marine Worm", "Polychaeta", "무척추동물", "바다,습지", "유기물과 작은 생물", "몸에 여러 마디가 있다.", "바다 바닥의 먹이그물에서 중요한 역할을 한다.", "일반", "Polychaete"),
    ("새우", "Shrimp", "Caridea", "무척추동물", "바다,연못", "유기물과 작은 생물", "몸이 여러 마디로 나뉜다.", "먹이그물에서 다양한 동물의 먹이가 된다.", "일반", "Shrimp"),
    ("게", "Crab", "Brachyura", "무척추동물", "바다,습지", "작은 동물과 유기물", "옆으로 걷는 행동이 특징적이다.", "단단한 외골격을 가지고 주기적으로 탈피한다.", "일반", "Crab"),

    # 식물
    ("소나무", "Korean Red Pine", "Pinus densiflora", "식물", "숲,산", "광합성", "바늘 모양 잎과 솔방울이 특징이다.", "상록 침엽수로 광합성을 통해 양분을 만든다.", "일반", "Pinus_densiflora"),
    ("은행나무", "Ginkgo", "Ginkgo biloba", "식물", "정원,산", "광합성", "부채 모양 잎이 특징이다.", "현존하는 은행나무류의 대표적인 종이다.", "희귀", "Ginkgo_biloba"),
    ("벚나무", "Cherry Blossom", "Prunus serrulata", "식물", "정원,숲", "광합성", "봄에 꽃이 피는 나무이다.", "꽃가루받이를 거쳐 열매를 맺는다.", "일반", "Prunus_serrulata"),
    ("민들레", "Dandelion", "Taraxacum officinale", "식물", "정원,초원", "광합성", "노란 꽃과 솜털 달린 열매가 특징이다.", "열매가 바람을 타고 퍼질 수 있다.", "일반", "Taraxacum_officinale"),
    ("해바라기", "Sunflower", "Helianthus annuus", "식물", "정원,초원", "광합성", "큰 꽃차례와 씨앗이 특징이다.", "꽃차례에는 작은 꽃들이 모여 있다.", "일반", "Helianthus_annuus"),
    ("연꽃", "Sacred Lotus", "Nelumbo nucifera", "식물", "연못,습지", "광합성", "넓은 잎과 큰 꽃을 가진 수생식물이다.", "잎 표면은 물을 잘 튕겨 내는 성질이 있다.", "희귀", "Nelumbo_nucifera"),
    ("수련", "Water Lily", "Nymphaea", "식물", "연못,습지", "광합성", "잎과 꽃이 물 위에 떠 있는 경우가 많다.", "물속 뿌리와 잎을 통해 수생 환경에 적응한다.", "일반", "Nymphaea"),
    ("고사리", "Bracken Fern", "Pteridium aquilinum", "식물", "숲,산", "광합성", "꽃 대신 포자로 번식한다.", "양치식물은 포자를 이용해 번식한다.", "일반", "Pteridium_aquilinum"),
    ("이끼", "Moss", "Bryophyta", "식물", "숲,산,습지", "광합성", "작고 촉촉한 곳에서 자라는 경우가 많다.", "물과 양분을 흡수하는 방식이 관다발식물과 다르다.", "일반", "Moss"),
    ("난초", "Orchid", "Orchidaceae", "식물", "숲,정원", "광합성", "꽃의 모양과 색이 매우 다양하다.", "일부 난초는 특정 곤충과 꽃가루받이 관계를 맺는다.", "희귀", "Orchidaceae"),
    ("선인장", "Cactus", "Cactaceae", "식물", "초원,정원", "광합성", "가시와 두꺼운 줄기가 특징이다.", "건조한 환경에서 물을 보존하는 데 적응했다.", "일반", "Cactaceae"),
    ("바오바브나무", "Baobab", "Adansonia", "식물", "초원", "광합성", "굵은 줄기에 물을 저장할 수 있다.", "건조한 지역의 환경에 적응한 나무이다.", "희귀", "Adansonia"),
    ("망고나무", "Mango", "Mangifera indica", "식물", "정원", "광합성", "달콤한 열매를 맺는다.", "꽃이 수정된 뒤 씨앗이 들어 있는 열매가 자란다.", "일반", "Mangifera_indica"),
    ("바나나", "Banana", "Musa", "식물", "정원", "광합성", "큰 잎과 길게 모여 달리는 열매가 특징이다.", "재배되는 바나나는 씨앗이 거의 없는 품종도 많다.", "일반", "Banana"),
    ("벼", "Rice", "Oryza sativa", "식물", "습지,초원", "광합성", "세계적으로 중요한 식량 작물이다.", "씨앗인 쌀에 탄수화물이 풍부하다.", "일반", "Rice"),
    ("밀", "Wheat", "Triticum aestivum", "식물", "초원", "광합성", "곡물의 대표적인 작물이다.", "밀가루는 빵과 면을 만드는 데 사용된다.", "일반", "Wheat"),
    ("대나무", "Bamboo", "Bambusoideae", "식물", "숲,산", "광합성", "줄기가 마디로 나뉘어 있다.", "나무처럼 보이지만 벼과에 속한다.", "일반", "Bamboo"),
    ("참나무", "Oak", "Quercus", "식물", "숲,산", "광합성", "도토리를 맺는 나무이다.", "열매는 여러 동물의 먹이가 된다.", "일반", "Oak"),
    ("단풍나무", "Maple", "Acer", "식물", "숲,산,정원", "광합성", "손바닥 모양 잎을 가진 종이 많다.", "날개 달린 열매가 바람을 타고 퍼진다.", "일반", "Maple"),
    ("갈대", "Common Reed", "Phragmites australis", "식물", "습지,연못", "광합성", "키가 크고 물가에 무리 지어 자란다.", "습지 생태계에서 서식처를 제공한다.", "일반", "Phragmites_australis"),
    ("해초", "Seagrass", "Zostera", "식물", "바다", "광합성", "바닷속에서 꽃을 피우는 식물이다.", "해양 생물의 서식처와 먹이를 제공한다.", "희귀", "Seagrass"),
    ("김", "Nori", "Pyropia", "조류", "바다", "광합성", "식용으로 이용되는 해조류이다.", "바다에서 광합성으로 양분을 만든다.", "일반", "Pyropia"),
    ("미역", "Wakame", "Undaria pinnatifida", "조류", "바다", "광합성", "갈색을 띠는 해조류이다.", "바다의 생산자로서 먹이그물에 참여한다.", "일반", "Undaria_pinnatifida"),

    # 균류와 작은 생물
    ("광대버섯", "Fly Agaric", "Amanita muscaria", "균류", "숲,산", "유기물과 공생 관계", "붉은 갓에 흰 점이 있는 버섯이다.", "독성이 있으므로 절대 먹으면 안 된다.", "희귀", "Amanita_muscaria"),
    ("표고버섯", "Shiitake", "Lentinula edodes", "균류", "숲", "죽은 나무의 유기물", "식용으로 재배되는 버섯이다.", "균사가 나무의 성분을 분해한다.", "일반", "Shiitake"),
    ("송이버섯", "Matsutake", "Tricholoma matsutake", "균류", "숲,산", "나무와의 공생 관계", "독특한 향으로 알려진 버섯이다.", "소나무와 공생 관계를 맺는다.", "초희귀", "Matsutake"),
    ("효모", "Baker's Yeast", "Saccharomyces cerevisiae", "균류", "정원", "당분", "빵을 부풀리는 데 이용된다.", "발효 과정에서 당을 분해해 이산화탄소를 만든다.", "희귀", "Saccharomyces_cerevisiae"),
    ("곰팡이", "Mold", "Aspergillus", "균류", "숲,정원", "유기물", "실처럼 뻗는 균사를 형성할 수 있다.", "유기물을 분해하는 종도 있지만 일부는 독소를 만들 수 있다.", "일반", "Aspergillus"),
    ("짚신벌레", "Paramecium", "Paramecium", "원생생물", "연못,습지", "세균과 작은 입자", "섬모를 이용해 움직인다.", "단세포 생물이며 섬모로 먹이를 모은다.", "희귀", "Paramecium"),
    ("아메바", "Amoeba", "Amoeba", "원생생물", "연못,습지", "작은 생물", "몸 모양이 계속 변한다.", "위족을 뻗어 이동하거나 먹이를 감싼다.", "희귀", "Amoeba"),
    ("규조류", "Diatom", "Bacillariophyta", "조류", "바다,연못", "광합성", "유리처럼 보이는 규산질 껍질을 가진다.", "수생 생태계에서 중요한 일차 생산자이다.", "희귀", "Diatom"),
    ("클로렐라", "Chlorella", "Chlorella vulgaris", "조류", "연못,습지", "광합성", "작은 단세포 녹조류이다.", "빛을 이용해 광합성을 한다.", "희귀", "Chlorella"),
    ("남세균", "Cyanobacteria", "Cyanobacteria", "세균", "연못,바다", "광합성", "광합성을 하는 세균 무리이다.", "지구의 산소 환경 형성에 중요한 역할을 했다.", "초희귀", "Cyanobacteria"),
    ("유산균", "Lactic Acid Bacteria", "Lactobacillus", "세균", "정원", "당분", "발효 식품을 만드는 데 이용된다.", "당을 발효해 젖산을 생성하는 종류가 있다.", "희귀", "Lactobacillus"),
    ("대장균", "Escherichia coli", "Escherichia coli", "세균", "정원", "영양분", "장내에 존재할 수 있는 세균이다.", "대부분의 균주는 해롭지 않지만 일부는 질병을 일으킨다.", "희귀", "Escherichia_coli"),
]


HABITATS = ["숲", "초원", "정원", "습지", "연못", "산", "바다"]

RARITY_WEIGHT = {
    "일반": 65,
    "희귀": 27,
    "초희귀": 8,
}

RARITY_XP = {
    "일반": 10,
    "희귀": 25,
    "초희귀": 60,
}

SPECIES = []
for idx, item in enumerate(RAW_SPECIES, start=1):
    name, english, latin, group, habitats, food, feature, science, rarity, wiki = item
    SPECIES.append({
        "id": idx,
        "name": name,
        "english": english,
        "latin": latin,
        "group": group,
        "habitat": habitats.split(","),
        "food": food,
        "feature": feature,
        "science": science,
        "rarity": rarity,
        "wiki": wiki,
    })


# =========================================================
# 이미지
# =========================================================

@st.cache_data(ttl=86400, show_spinner=False)
def get_wikipedia_info(title):
    """위키백과 요약 정보에서 이미지 주소를 가져온다."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    headers = {"User-Agent": "BioHunterApp/1.0 (educational project)"}

    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            data = response.json()
            return {
                "image": data.get("thumbnail", {}).get("source"),
                "description": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            }
    except requests.RequestException:
        pass
    except ValueError:
        pass

    return {"image": None, "description": "", "url": None}


def show_species_image(species, width=None):
    info = get_wikipedia_info(species["wiki"])
    if info["image"]:
        st.image(info["image"], use_container_width=True)
    else:
        st.markdown(
            f"<div style='font-size:90px;text-align:center;padding:25px;'>"
            f"{species.get('emoji', '🌿')}</div>",
            unsafe_allow_html=True,
        )
        st.caption("사진을 불러오지 못했어요. 인터넷 연결을 확인해 주세요.")

    if info["url"]:
        st.markdown(f"[위키백과에서 더 알아보기]({info['url']})")


# =========================================================
# 세션 상태
# =========================================================

def init_state():
    defaults = {
        "collection": {},
        "discovery_log": [],
        "xp": 0,
        "found_total": 0,
        "quiz_score": 0,
        "quiz_attempts": 0,
        "completed_achievements": [],
        "last_found": None,
        "quiz_question": None,
        "quiz_answered": False,
        "quiz_feedback": "",
        "quiz_correct": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def get_level(xp):
    return xp // 100 + 1


def get_next_level_xp(xp):
    return get_level(xp) * 100


def get_species_by_id(species_id):
    return next((s for s in SPECIES if s["id"] == species_id), None)


def discover_species(habitat):
    possible = [s for s in SPECIES if habitat in s["habitat"]]
    if not possible:
        possible = SPECIES[:]

    weights = [RARITY_WEIGHT.get(s["rarity"], 1) for s in possible]
    found = random.choices(possible, weights=weights, k=1)[0]

    species_id = found["id"]
    collection = st.session_state.collection

    if species_id in collection:
        collection[species_id]["count"] += 1
        gained_xp = 3
        message = "이미 발견한 생물이에요! 중복 발견 보너스 경험치 +3"
    else:
        collection[species_id] = {"count": 1}
        gained_xp = RARITY_XP.get(found["rarity"], 10)
        message = f"새로운 생물을 도감에 등록했어요! 경험치 +{gained_xp}"

    st.session_state.xp += gained_xp
    st.session_state.found_total += 1
    st.session_state.last_found = {
        "species": found,
        "message": message,
    }

    st.session_state.discovery_log.insert(0, {
        "name": found["name"],
        "habitat": habitat,
        "rarity": found["rarity"],
    })
    st.session_state.discovery_log = st.session_state.discovery_log[:20]


# =========================================================
# 업적
# =========================================================

ACHIEVEMENTS = [
    {
        "id": "first",
        "name": "첫 발견",
        "description": "생물을 처음으로 발견하기",
        "check": lambda: len(st.session_state.collection) >= 1,
        "reward": 10,
    },
    {
        "id": "five",
        "name": "초보 탐험가",
        "description": "서로 다른 생물 5종 모으기",
        "check": lambda: len(st.session_state.collection) >= 5,
        "reward": 20,
    },
    {
        "id": "ten",
        "name": "생물 관찰가",
        "description": "서로 다른 생물 10종 모으기",
        "check": lambda: len(st.session_state.collection) >= 10,
        "reward": 30,
    },
    {
        "id": "twenty",
        "name": "자연 연구원",
        "description": "서로 다른 생물 20종 모으기",
        "check": lambda: len(st.session_state.collection) >= 20,
        "reward": 50,
    },
    {
        "id": "allhabitats",
        "name": "환경 탐험가",
        "description": "7개 서식지에서 모두 탐험하기",
        "check": lambda: len(set(x["habitat"] for x in st.session_state.discovery_log)) >= 7,
        "reward": 40,
    },
    {
        "id": "quiz",
        "name": "생물 퀴즈 도전자",
        "description": "퀴즈에서 3문제 이상 정답 맞히기",
        "check": lambda: st.session_state.quiz_score >= 3,
        "reward": 30,
    },
]


def check_achievements():
    for achievement in ACHIEVEMENTS:
        if (
            achievement["id"] not in st.session_state.completed_achievements
            and achievement["check"]()
        ):
            st.session_state.completed_achievements.append(achievement["id"])
            st.session_state.xp += achievement["reward"]
            st.toast(
                f"🏆 업적 달성: {achievement['name']}! 경험치 +{achievement['reward']}",
                icon="🎉",
            )


# =========================================================
# 상단 화면
# =========================================================

level = get_level(st.session_state.xp)
progress = (st.session_state.xp % 100) / 100

st.markdown("""
<div class="hero">
    <h1>🌿 바이오 헌터</h1>
    <p>탐험하고, 발견하고, 생물 도감을 완성해 보자!</p>
</div>
""", unsafe_allow_html=True)

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("🧬 도감 등록", f"{len(st.session_state.collection)}종")
metric2.metric("🔎 누적 발견", f"{st.session_state.found_total}회")
metric3.metric("⭐ 레벨", f"Lv. {level}")
metric4.metric("✨ 경험치", st.session_state.xp)

st.progress(progress, text=f"다음 레벨까지 {100 - (st.session_state.xp % 100)} XP")


# =========================================================
# 메뉴
# =========================================================

tab_explore, tab_dex, tab_mission, tab_quiz, tab_about = st.tabs([
    "🧭 탐험",
    "📖 생물 도감",
    "🏆 업적",
    "🧠 생물 퀴즈",
    "ℹ️ 게임 안내",
])


# =========================================================
# 탐험
# =========================================================

with tab_explore:
    st.subheader("어디를 탐험할까?")
    st.write("서식지를 선택하고 생물을 발견해 보세요.")

    selected_habitat = st.selectbox(
        "탐험할 서식지",
        HABITATS,
        key="selected_habitat",
    )

    habitat_emojis = {
        "숲": "🌳",
        "초원": "🌾",
        "정원": "🌷",
        "습지": "🪷",
        "연못": "🐸",
        "산": "⛰️",
        "바다": "🌊",
    }

    possible_count = sum(
        1 for s in SPECIES if selected_habitat in s["habitat"]
    )

    st.markdown(
        f"<div class='info-card'>"
        f"<h3>{habitat_emojis[selected_habitat]} {selected_habitat} 탐험</h3>"
        f"<p>이 서식지에서 발견할 수 있도록 설정된 생물: "
        f"<b>{possible_count}종</b></p>"
        f"<p class='small-note'>희귀도에 따라 발견 확률이 달라집니다.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔍 생물 발견하기", type="primary", use_container_width=True):
        discover_species(selected_habitat)
        check_achievements()
        st.rerun()

    if st.session_state.last_found:
        found_data = st.session_state.last_found
        found = found_data["species"]

        st.divider()
        st.subheader("🎉 발견한 생물!")

        left, right = st.columns([1, 1])

        with left:
            show_species_image(found)

        with right:
            st.markdown(f"## {found['name']}")
            st.write(f"**영문명:** {found['english']}")
            st.write(f"**학명:** *{found['latin']}*")
            st.write(f"**분류:** {found['group']}")
            st.write(f"**희귀도:** {found['rarity']}")
            st.write(f"**먹이:** {found['food']}")
            st.write(f"**특징:** {found['feature']}")
            st.info(found_data["message"])

            if found["rarity"] == "초희귀":
                st.balloons()

        with st.expander("🔬 생물학 정보 더 보기"):
            st.write(found["science"])

    st.divider()
    st.subheader("🕵️ 최근 탐험 기록")

    if st.session_state.discovery_log:
        for log in st.session_state.discovery_log[:8]:
            st.write(
                f"• {log['name']} — {log['habitat']} / {log['rarity']}"
            )
    else:
        st.caption("아직 발견 기록이 없어요. 첫 탐험을 시작해 보세요!")


# =========================================================
# 생물 도감
# =========================================================

with tab_dex:
    st.subheader("📖 나의 생물 도감")

    total_species = len(SPECIES)
    registered = len(st.session_state.collection)
    st.progress(
        registered / total_species,
        text=f"도감 완성도: {registered} / {total_species}종",
    )

    search = st.text_input(
        "🔎 생물 이름 검색",
        placeholder="예: 나비, 소나무, 문어",
    )

    group_options = ["전체"] + sorted(set(s["group"] for s in SPECIES))
    selected_group = st.selectbox("분류 선택", group_options)

    status_filter = st.radio(
        "도감 보기",
        ["전체", "발견한 생물", "아직 발견하지 못한 생물"],
        horizontal=True,
    )

    filtered_species = []

    for species in SPECIES:
        discovered = species["id"] in st.session_state.collection

        if search and search.lower() not in (
            species["name"] + " " + species["english"] + " " + species["latin"]
        ).lower():
            continue

        if selected_group != "전체" and species["group"] != selected_group:
            continue

        if status_filter == "발견한 생물" and not discovered:
            continue

        if status_filter == "아직 발견하지 못한 생물" and discovered:
            continue

        filtered_species.append(species)

    st.caption(f"검색 결과: {len(filtered_species)}종")

    if not filtered_species:
        st.info("조건에 맞는 생물이 없어요.")
    else:
        for start in range(0, len(filtered_species), 3):
            row_species = filtered_species[start:start + 3]
            cols = st.columns(3)

            for col, species in zip(cols, row_species):
                discovered = species["id"] in st.session_state.collection

                with col:
                    with st.container(border=True):
                        if discovered:
                            info = get_wikipedia_info(species["wiki"])
                            if info["image"]:
                                st.image(info["image"], use_container_width=True)
                            else:
                                st.markdown(
                                    "<div style='font-size:55px;text-align:center'>🌿</div>",
                                    unsafe_allow_html=True,
                                )
                            st.markdown(f"### {species['name']}")
                            st.caption(species["english"])
                            st.caption(f"학명: *{species['latin']}*")
                            st.write(f"**분류:** {species['group']}")
                            st.write(f"**희귀도:** {species['rarity']}")
                            st.write(f"**먹이:** {species['food']}")
                            st.write(f"**특징:** {species['feature']}")
                            st.write(f"**생물학 정보:** {species['science']}")
                            count = st.session_state.collection[species["id"]]["count"]
                            st.success(f"발견 횟수: {count}회")
                        else:
                            st.markdown(
                                "<div style='font-size:60px;text-align:center'>❔</div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown("### 미발견 생물")
                            st.write("탐험을 통해 발견해 보세요.")
                            st.caption(f"분류: {species['group']}")
                            st.caption(f"서식지: {', '.join(species['habitat'])}")


# =========================================================
# 업적
# =========================================================

with tab_mission:
    st.subheader("🏆 탐험 업적")
    st.write("조건을 달성하면 보너스 경험치를 받을 수 있어요.")

    check_achievements()

    for achievement in ACHIEVEMENTS:
        done = achievement["id"] in st.session_state.completed_achievements

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"### {'✅' if done else '🔒'} {achievement['name']}"
                )
                st.write(achievement["description"])
                st.caption(f"보상: 경험치 +{achievement['reward']}")

            with col2:
                st.write("달성!" if done else "도전 중")


# =========================================================
# 생물 퀴즈
# =========================================================

QUIZZES = [
    {
        "question": "광합성을 통해 양분을 만드는 생물은?",
        "options": ["소나무", "여우", "문어", "버섯"],
        "answer": "소나무",
        "explanation": "소나무는 빛에너지를 이용해 광합성을 하는 식물입니다.",
    },
    {
        "question": "다음 중 곤충의 특징으로 알맞은 것은?",
        "options": ["다리가 6개이다", "다리가 8개이다", "지느러미가 있다", "젖을 먹인다"],
        "answer": "다리가 6개이다",
        "explanation": "곤충은 일반적으로 머리, 가슴, 배로 몸이 나뉘고 다리가 3쌍입니다.",
    },
    {
        "question": "다음 중 양서류에 속하는 생물은?",
        "options": ["청개구리", "참새", "도마뱀", "잉어"],
        "answer": "청개구리",
        "explanation": "개구리는 양서류입니다. 많은 양서류는 물과 육지 모두에서 생활합니다.",
    },
    {
        "question": "효모가 빵을 부풀리는 데 중요한 과정은?",
        "options": ["발효", "광합성", "증산", "수분 흡수만 일어나는 과정"],
        "answer": "발효",
        "explanation": "효모는 당을 분해하면서 이산화탄소를 만들어 반죽을 부풀립니다.",
    },
    {
        "question": "다음 중 포유류는?",
        "options": ["수달", "물총새", "문어", "소나무"],
        "answer": "수달",
        "explanation": "수달은 새끼에게 젖을 먹이는 포유류입니다.",
    },
    {
        "question": "해마에 대한 설명으로 알맞은 것은?",
        "options": ["수컷이 알을 품는 육아낭이 있다", "포유류이다", "날개로 난다", "육지에서만 산다"],
        "answer": "수컷이 알을 품는 육아낭이 있다",
        "explanation": "해마는 물고기이며 수컷이 육아낭에서 알을 보호합니다.",
    },
    {
        "question": "버섯은 어느 분류에 속할까?",
        "options": ["균류", "식물", "동물", "파충류"],
        "answer": "균류",
        "explanation": "버섯은 식물이 아니라 균류에 속합니다.",
    },
    {
        "question": "다음 중 물속에서 생활하는 포유류는?",
        "options": ["돌고래", "상어", "문어", "해파리"],
        "answer": "돌고래",
        "explanation": "돌고래는 물속에서 생활하지만 공기로 호흡하는 포유류입니다.",
    },
    {
        "question": "꽃가루받이를 돕는 대표적인 곤충은?",
        "options": ["꿀벌", "지렁이", "문어", "도롱뇽"],
        "answer": "꿀벌",
        "explanation": "꿀벌은 꽃을 방문하면서 꽃가루를 옮기는 역할을 합니다.",
    },
    {
        "question": "다음 중 포자로 번식하는 식물은?",
        "options": ["고사리", "벚나무", "벼", "해바라기"],
        "answer": "고사리",
        "explanation": "고사리는 꽃과 씨앗 대신 포자를 이용해 번식합니다.",
    },
    {
        "question": "산호초 생태계에 대한 설명으로 알맞은 것은?",
        "options": ["많은 해양 생물의 서식처가 된다", "모두 민물에서 산다", "식물만 살 수 있다", "생물 다양성이 낮다"],
        "answer": "많은 해양 생물의 서식처가 된다",
        "explanation": "산호초는 다양한 해양 생물이 살아가는 중요한 서식처입니다.",
    },
    {
        "question": "다음 중 광합성을 하는 세균 무리는?",
        "options": ["남세균", "효모", "대장균", "유산균"],
        "answer": "남세균",
        "explanation": "남세균은 광합성을 할 수 있는 세균 무리입니다.",
    },
]


def new_quiz():
    st.session_state.quiz_question = random.choice(QUIZZES)
    st.session_state.quiz_answered = False
    st.session_state.quiz_feedback = ""
    st.session_state.quiz_correct = False


with tab_quiz:
    st.subheader("🧠 생물 퀴즈")
    st.write("문제를 풀어 생물 지식을 확인해 보세요.")

    st.metric("정답 수", st.session_state.quiz_score)
    st.caption(f"도전한 문제 수: {st.session_state.quiz_attempts}")

    if st.session_state.quiz_question is None:
        if st.button("퀴즈 시작하기", type="primary"):
            new_quiz()
            st.rerun()

    else:
        question = st.session_state.quiz_question

        with st.container(border=True):
            st.markdown(f"### {question['question']}")

            selected_answer = st.radio(
                "정답을 선택하세요.",
                question["options"],
                key=f"quiz_{id(question)}",
                disabled=st.session_state.quiz_answered,
            )

            if not st.session_state.quiz_answered:
                if st.button("정답 확인", type="primary"):
                    st.session_state.quiz_attempts += 1
                    correct = selected_answer == question["answer"]
                    st.session_state.quiz_correct = correct
                    st.session_state.quiz_answered = True

                    if correct:
                        st.session_state.quiz_score += 1
                        st.session_state.xp += 10
                        st.session_state.quiz_feedback = (
                            "정답입니다! 경험치 +10\n\n" + question["explanation"]
                        )
                    else:
                        st.session_state.quiz_feedback = (
                            f"아쉽지만 정답은 **{question['answer']}**입니다.\n\n"
                            + question["explanation"]
                        )

                    check_achievements()
                    st.rerun()

        if st.session_state.quiz_answered:
            if st.session_state.quiz_correct:
                st.success(st.session_state.quiz_feedback)
            else:
                st.warning(st.session_state.quiz_feedback)

            if st.button("다음 문제"):
                new_quiz()
                st.rerun()


# =========================================================
# 게임 안내
# =========================================================

with tab_about:
    st.subheader("ℹ️ 바이오 헌터 안내")

    st.markdown("""
### 🌱 게임 목표
여러 서식지를 탐험하면서 다양한 생물을 발견하고 도감을 완성해 보세요.

### 🔎 탐험 방법
1. 탐험 탭에서 서식지를 선택합니다.
2. 생물 발견하기를 누릅니다.
3. 발견한 생물의 사진과 특징을 확인합니다.
4. 도감에서 수집한 생물을 다시 살펴봅니다.

### ⭐ 희귀도와 경험치
- **일반:** 발견하면 경험치 10
- **희귀:** 발견하면 경험치 25
- **초희귀:** 발견하면 경험치 60
- **중복 발견:** 경험치 3

### 📚 생물 정보
생물 정보는 학습용으로 정리한 내용입니다. 실제 서식지와 분포는 종과 지역에 따라 다를 수 있습니다. 사진은 위키백과에서 불러오며, 모든 생물의 사진이 항상 제공되는 것은 아닙니다.

### 💾 저장 안내
현재 버전은 별도 데이터베이스 없이 Streamlit 세션에 기록을 보관합니다. 앱이 재시작되거나 세션이 초기화되면 수집 기록이 사라질 수 있습니다.
    """)

    st.divider()
    st.write(f"현재 등록된 생물 데이터: **{len(SPECIES)}종**")
    st.write(f"현재 퀴즈 문제: **{len(QUIZZES)}개**")


# =========================================================
# 하단 안내
# =========================================================

st.divider()
st.markdown(
    "<p style='text-align:center;color:#718071;'>"
    "🌿 BIO HUNTER · 생물 다양성을 탐험하는 작은 도감"
    "</p>",
    unsafe_allow_html=True,
)
