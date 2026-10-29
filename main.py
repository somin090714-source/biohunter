
import random
import requests
import streamlit as st
from urllib.parse import quote

# =========================================================
# 바이오 헌터 - 탐험하며 생명과학 퀴즈를 풀고 생물을 수집하는 게임
# =========================================================

st.set_page_config(
    page_title="바이오 헌터",
    page_icon="🌿",
    layout="wide",
)

# -------------------- 디자인 --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f4f8ed 0%, #fffdf5 100%);
}
h1, h2, h3 {
    color: #28583a;
}
div.stButton > button {
    border-radius: 12px;
    min-height: 43px;
    font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background-color: #39764c;
    border-color: #39764c;
}
.creature-box {
    background: white;
    border: 1px solid #dce8d4;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
}
.small-note {
    color: #667766;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------- 지형 설정 --------------------

TERRAINS = {
    "숲": {"emoji": "🌲", "habitats": ["숲"], "description": "나무와 숲속 생물"},
    "호수·연못": {
        "emoji": "🏞️",
        "habitats": ["호수", "연못"],
        "description": "물속과 물가의 생물",
    },
    "바다": {"emoji": "🌊", "habitats": ["바다"], "description": "바다에 사는 생물"},
    "산": {"emoji": "⛰️", "habitats": ["산"], "description": "산과 바위 주변의 생물"},
    "초원": {"emoji": "🌾", "habitats": ["초원"], "description": "풀밭과 들판의 생물"},
    "습지": {"emoji": "🐸", "habitats": ["습지"], "description": "늪과 습지의 생물"},
}

RARITY_INFO = {
    "일반": {"weight": 58, "xp": 10, "emoji": "🍃", "color": "일반"},
    "고급": {"weight": 25, "xp": 20, "emoji": "🌿", "color": "고급"},
    "희귀": {"weight": 12, "xp": 40, "emoji": "💎", "color": "희귀"},
    "초희귀": {"weight": 4, "xp": 80, "emoji": "✨", "color": "초희귀"},
    "전설": {"weight": 1, "xp": 150, "emoji": "👑", "color": "전설"},
}

# 생물 데이터 형식:
# 한국어 이름|영어 이름|분류|서식지|희귀도|설명|대표 이모지
RAW_SPECIES = """
참개구리|Black-spotted pond frog|양서류|연못,습지|일반|논과 연못 주변에서 볼 수 있는 개구리|🐸
청개구리|Japanese tree frog|양서류|숲,습지|고급|나뭇잎과 풀 위에서 생활하는 작은 개구리|🐸
도롱뇽|Korean salamander|양서류|숲,습지|고급|축축한 숲 바닥과 물가에서 발견되는 양서류|🦎
맹꽁이|Korean narrow-mouthed frog|양서류|초원,습지|희귀|비가 오는 시기에 땅속에서 나와 활동하는 개구리|🐸
금개구리|Seoul pond frog|양서류|연못,습지|희귀|습지와 논 주변에서 살아가는 우리나라의 개구리|🐸
두꺼비|Asian common toad|양서류|숲,초원|일반|건조한 곳에서도 비교적 잘 살아가는 양서류|🐸
산개구리|Rana dybowskii|양서류|산,숲|고급|산지 계곡과 숲 주변에서 볼 수 있는 개구리|🐸
수달|Eurasian otter|포유류|호수,연못,습지|희귀|물고기를 잡아먹으며 물가에서 생활하는 포유류|🦦
고라니|Water deer|포유류|숲,습지|일반|우리나라의 숲과 풀밭에서 볼 수 있는 사슴과 동물|🦌
너구리|Raccoon dog|포유류|숲,산|일반|숲과 산 주변에서 다양한 먹이를 먹는 포유류|🦝
오소리|Asian badger|포유류|숲,산|고급|땅을 파서 굴을 만들고 생활하는 포유류|🦡
멧돼지|Wild boar|포유류|숲,산|고급|잡식성이며 숲속을 돌아다니며 먹이를 찾는 동물|🐗
다람쥐|Siberian chipmunk|포유류|숲,산|일반|도토리와 씨앗 등을 모아 먹는 작은 포유류|🐿️
청설모|Red squirrel|포유류|숲|일반|나무를 잘 타며 열매와 씨앗을 먹는 동물|🐿️
산양|Long-tailed goral|포유류|산|초희귀|가파른 바위산에서 생활하는 초식동물|🐐
삵|Leopard cat|포유류|숲,습지|희귀|우리나라에 서식하는 야생 고양잇과 동물|🐈
하늘다람쥐|Siberian flying squirrel|포유류|숲|희귀|몸 옆의 막을 이용해 나무 사이를 활공하는 동물|🐿️
담비|Yellow-throated marten|포유류|숲,산|희귀|숲에서 작은 동물과 열매를 먹는 포유류|🦦
고슴도치|Amur hedgehog|포유류|숲,초원|고급|등에 난 가시로 몸을 보호하는 작은 포유류|🦔
박쥐|Bat|포유류|숲,산|고급|날개로 날며 많은 종류가 밤에 활동하는 포유류|🦇
참새|Eurasian tree sparrow|조류|숲,초원|일반|사람이 사는 곳 주변에서도 흔히 볼 수 있는 작은 새|🐦
까치|Oriental magpie|조류|숲,초원|일반|검은색과 흰색 깃털이 특징인 새|🐦
까마귀|Carrion crow|조류|숲,산|일반|뛰어난 학습 능력을 보이는 새|🐦‍⬛
박새|Japanese tit|조류|숲|일반|나무 사이를 오가며 곤충을 잡아먹는 작은 새|🐦
물총새|Common kingfisher|조류|호수,연못|고급|물속으로 뛰어들어 물고기를 잡는 새|🐦
왜가리|Grey heron|조류|호수,연못,습지|고급|긴 다리로 물가를 걸으며 물고기를 사냥하는 새|🪶
백로|Egret|조류|호수,연못,습지|고급|흰 깃털과 긴 다리가 특징인 물새|🪶
원앙|Mandarin duck|조류|호수,연못|희귀|수컷의 화려한 깃털이 특징인 오리류|🦆
수리부엉이|Eurasian eagle-owl|조류|숲,산|희귀|큰 눈과 귀깃이 특징인 야행성 맹금류|🦉
황조롱이|Common kestrel|조류|초원,산|고급|공중에서 정지 비행을 하며 먹이를 찾는 맹금류|🦅
큰고니|Whooper swan|조류|호수,연못,습지|희귀|겨울철 물가에서 관찰할 수 있는 큰 물새|🦢
노랑부리저어새|Eurasian spoonbill|조류|습지|희귀|주걱처럼 생긴 부리로 물속 먹이를 찾는 새|🪶
후투티|Eurasian hoopoe|조류|초원,숲|고급|머리의 독특한 깃털 장식이 눈에 띄는 새|🐦
딱따구리|Great spotted woodpecker|조류|숲|고급|나무를 두드려 곤충을 찾는 새|🐦
제비|Barn swallow|조류|초원,습지|일반|날면서 곤충을 잡아먹는 새|🐦
꿩|Common pheasant|조류|초원,숲|일반|땅 위에서 먹이를 찾는 꿩과의 새|🐦
잉어|Common carp|어류|호수,연못|일반|민물에서 생활하며 다양한 먹이를 먹는 물고기|🐟
붕어|Carassius auratus|어류|호수,연못|일반|연못과 호수에서 흔히 볼 수 있는 민물고기|🐟
피라미|Zacco platypus|어류|호수,연못|일반|하천과 물가에서 무리 지어 생활하는 작은 물고기|🐟
미꾸라지|Oriental weatherfish|어류|호수,연못,습지|일반|진흙이 있는 얕은 물에서 생활하는 물고기|🐟
메기|Amur catfish|어류|호수,연못|고급|입 주변의 수염으로 먹이를 찾는 민물고기|🐟
쏘가리|Mandarin fish|어류|호수,연못|고급|다른 물고기를 잡아먹는 민물고기|🐟
은어|Plecoglossus altivelis|어류|호수,연못|고급|맑은 물에서 생활하며 바위의 조류를 먹는 물고기|🐟
연어|Salmon|어류|바다|고급|성장한 뒤 바다에서 생활하고 산란기에 강으로 돌아오는 물고기|🐟
장어|Japanese eel|어류|호수,연못,바다|희귀|성장 단계에 따라 서식 환경이 달라지는 물고기|🐟
철갑상어|Sturgeon|어류|바다|희귀|단단한 골판이 몸을 덮고 있는 물고기 무리|🐟
꺽지|Korean aucha perch|어류|호수,연못|고급|우리나라의 맑은 하천에서 볼 수 있는 민물고기|🐟
빙어|Japanese smelt|어류|호수,연못|고급|차가운 호수에서 생활하는 작은 물고기|🐟
가물치|Northern snakehead|어류|호수,연못,습지|고급|산소가 부족한 환경에서도 잘 견디는 물고기|🐟
복어|Pufferfish|어류|바다|고급|위협을 받으면 몸을 부풀리는 물고기|🐡
흰동가리|Ocellaris clownfish|어류|바다|고급|말미잘과 함께 생활하는 주황색 물고기|🐠
혹등고래|Humpback whale|포유류|바다|전설|긴 가슴지느러미와 도약 행동으로 알려진 대형 고래|🐋
점박이물범|Spotted seal|포유류|바다|희귀|몸에 점무늬가 있는 바다 포유류|🦭
남방큰돌고래|Indo-Pacific bottlenose dolphin|포유류|바다|희귀|제주도 주변 바다에서 관찰되는 돌고래|🐬
바다거북|Sea turtle|파충류|바다|희귀|바다에서 생활하며 알을 낳을 때 육지로 올라오는 파충류|🐢
푸른바다거북|Green sea turtle|파충류|바다|희귀|해초와 해조류 등을 먹는 바다거북|🐢
남생이|Reeves's turtle|파충류|연못,습지|희귀|민물에서 생활하는 우리나라의 토종 거북|🐢
자라|Chinese softshell turtle|파충류|호수,연못|고급|부드러운 가죽 같은 등딱지가 특징인 거북|🐢
살모사|Sakishima habu|파충류|숲,산|희귀|독을 가진 뱀으로 야생에서 주의해야 하는 동물|🐍
구렁이|Rat snake|파충류|숲,산|고급|몸이 길고 주로 작은 동물을 먹는 뱀|🐍
도마뱀|Lizard|파충류|숲,산|일반|비늘로 덮인 피부를 가진 파충류|🦎
꿀벌|Honey bee|곤충|숲,초원|일반|꽃가루받이를 돕고 꿀을 만드는 사회성 곤충|🐝
호랑나비|Asian swallowtail|곤충|숲,초원|고급|노란색과 검은색 무늬가 특징인 나비|🦋
장수풍뎅이|Japanese rhinoceros beetle|곤충|숲|고급|수컷의 큰 뿔이 특징인 딱정벌레|🪲
사슴벌레|Stag beetle|곤충|숲|고급|큰 턱으로 알려진 딱정벌레|🪲
무당벌레|Ladybird beetle|곤충|숲,초원|일반|작은 진딧물 등을 먹는 딱정벌레|🐞
잠자리|Dragonfly|곤충|호수,연못,습지|일반|날개가 두 쌍이며 날아다니는 곤충|🪰
반딧불이|Firefly|곤충|숲,습지|희귀|빛을 내는 발광 기관이 있는 곤충|✨
사마귀|Praying mantis|곤충|초원,숲|고급|앞다리로 먹이를 붙잡는 포식성 곤충|🦗
장수잠자리|Giant darner|곤충|연못,습지|고급|큰 몸과 빠른 비행이 특징인 잠자리|🪰
물방개|Great diving beetle|곤충|연못,습지|일반|뒷다리를 이용해 물속을 헤엄치는 수서곤충|🪲
물자라|Appasus japonicus|곤충|연못,습지|고급|물속에서 작은 동물을 사냥하는 곤충|🪲
왕잠자리|Common green darner|곤충|연못,습지|고급|연못 주변에서 빠르게 날아다니는 잠자리|🪰
길앞잡이|Tiger beetle|곤충|초원,산|고급|빠르게 달리며 작은 곤충을 사냥하는 딱정벌레|🪲
제비나비|Chinese windmill|곤충|숲,초원|고급|검은 날개와 꼬리 모양 돌기가 특징인 나비|🦋
큰줄흰나비|Large white butterfly|곤충|초원|일반|흰 날개에 검은 무늬가 있는 나비|🦋
민들레|Dandelion|식물|초원|일반|씨앗이 바람을 타고 퍼지는 꽃식물|🌼
소나무|Japanese red pine|식물|숲,산|일반|바늘 모양 잎을 가진 상록수|🌲
은행나무|Ginkgo biloba|식물|숲,초원|일반|부채 모양 잎을 가진 나무|🌳
벚나무|Cherry blossom|식물|숲,산|일반|봄에 꽃을 피우는 나무|🌸
해바라기|Sunflower|식물|초원|일반|큰 꽃과 씨앗으로 잘 알려진 식물|🌻
연꽃|Sacred lotus|식물|연못,습지|고급|물 위로 잎과 꽃을 높이 올리는 수생식물|🪷
끈끈이주걱|Sundew|식물|습지|희귀|끈끈한 잎으로 작은 곤충을 붙잡는 식충식물|🌱
파리지옥|Venus flytrap|식물|습지|희귀|잎을 빠르게 닫아 작은 먹이를 붙잡는 식물|🌿
주목|Japanese yew|식물|산,숲|고급|늘푸른 잎을 가진 나무로 씨앗 주변에 붉은 구조가 생김|🌲
으름덩굴|Akebia quinata|식물|숲|일반|덩굴로 자라며 열매가 열리는 식물|🌿
산철쭉|Rhododendron yedoense|식물|산|일반|봄에 분홍색 계열의 꽃을 피우는 관목|🌺
억새|Silver grass|식물|초원,산|일반|가을에 은빛 꽃차례가 돋보이는 풀|🌾
갈대|Common reed|식물|습지,연못|일반|물가와 습지에서 무리 지어 자라는 키 큰 풀|🌾
부들|Broadleaf cattail|식물|습지,연못|일반|갈색의 길쭉한 꽃차례가 특징인 습지식물|🌱
수련|Water lily|식물|연못,습지|일반|물 위에 둥근 잎과 꽃을 띄우는 수생식물|🪷
검정말|Hydrilla|식물|연못|일반|물속에서 자라며 작은 수생동물의 서식처가 되는 식물|🌿
갯메꽃|Beach morning glory|식물|바다|일반|해안 모래땅에서 자라는 덩굴식물|🌸
갯완두|Beach pea|식물|바다|일반|해안 모래땅에서 자라며 자주색 꽃을 피우는 식물|🌱
"""

SPECIES = []
for line in RAW_SPECIES.strip().splitlines():
    parts = [part.strip() for part in line.split("|")]
    if len(parts) == 7:
        name, english, category, habitat, rarity, description, emoji = parts
        SPECIES.append({
            "name": name,
            "english": english,
            "category": category,
            "habitat": habitat.split(","),
            "rarity": rarity,
            "description": description,
            "emoji": emoji,
        })

SPECIES_BY_NAME = {item["name"]: item for item in SPECIES}

# -------------------- 생명과학 퀴즈 --------------------
# 희귀도가 높을수록 더 어려운 문제 묶음을 사용한다.
# 각 문항은 질문, 보기 4개, 정답 번호, 해설 순서이다.

QUIZZES = {
    "일반": [
        ("식물이 광합성을 할 때 주로 흡수하는 기체는?",
         ["산소", "이산화탄소", "질소", "수소"], 1,
         "식물은 빛에너지를 이용해 이산화탄소와 물로 유기물을 만듭니다."),
        ("동물이 숨을 쉴 때 에너지 생산에 주로 이용되는 기체는?",
         ["산소", "헬륨", "수소", "네온"], 0,
         "많은 동물은 세포 호흡에 산소를 이용해 에너지를 얻습니다."),
        ("먹이사슬에서 식물의 일반적인 역할은?",
         ["분해자", "생산자", "최상위 포식자", "기생생물"], 1,
         "식물은 광합성으로 스스로 유기물을 만들어 생산자 역할을 합니다."),
        ("동물의 몸을 지탱하고 보호하는 역할을 하는 구조는?",
         ["뼈", "엽록체", "꽃가루", "뿌리털"], 0,
         "척추동물의 뼈는 몸을 지탱하고 내부 기관을 보호합니다."),
        ("식물의 뿌리가 주로 하는 일은?",
         ["빛을 감지해 이동하기", "물과 무기 양분 흡수", "소리 내기", "산소만 만들기"], 1,
         "뿌리는 토양에서 물과 무기 양분을 흡수하는 중요한 역할을 합니다."),
    ],
    "고급": [
        ("광합성이 주로 일어나는 세포 소기관은?",
         ["미토콘드리아", "엽록체", "리보솜", "핵"], 1,
         "엽록체에는 빛에너지를 흡수하는 색소가 있어 광합성이 일어납니다."),
        ("먹이사슬에서 에너지가 상위 영양 단계로 전달될 때 일반적으로 나타나는 현상은?",
         ["에너지가 모두 전달된다", "일부 에너지가 생명 활동과 열로 소모된다",
          "에너지가 새로 만들어진다", "에너지가 사라지지 않고 전부 축적된다"], 1,
         "생명 활동에 에너지가 사용되며 일부는 열로 방출되므로 다음 단계로 전달되는 에너지는 줄어듭니다."),
        ("양서류의 일반적인 특징으로 가장 알맞은 것은?",
         ["모든 종이 평생 바다에서 산다", "생활사에서 물과 육지 환경을 이용하는 종이 많다",
          "몸이 깃털로 덮여 있다", "모든 종이 알을 낳지 않는다"], 1,
         "많은 양서류는 물속에서 유생 시기를 보내고 성장하면서 육지에서도 생활합니다."),
        ("생태계에서 분해자의 중요한 역할은?",
         ["태양빛을 직접 만든다", "죽은 생물의 물질을 분해해 물질 순환에 기여한다",
          "모든 생산자를 없앤다", "먹이사슬을 중단시킨다"], 1,
         "분해자는 사체와 배설물 등을 분해해 물질이 생태계에서 다시 순환하도록 돕습니다."),
        ("꽃식물에서 씨앗이 만들어지는 과정과 가장 밀접한 것은?",
         ["수분과 수정", "세포 호흡의 중단", "잎의 탈락", "뿌리의 광합성"], 0,
         "꽃가루가 암술머리에 옮겨지는 수분 뒤 수정이 일어나면 씨앗이 발달할 수 있습니다."),
    ],
    "희귀": [
        ("생태계의 생물 다양성을 높게 유지하는 것의 중요한 의미는?",
         ["모든 생물이 같은 먹이를 먹게 한다",
          "환경 변화에 대응할 수 있는 생태계의 가능성을 높인다",
          "분해자의 역할을 없앤다",
          "생태계에서 에너지 이동을 멈춘다"], 1,
         "다양한 생물과 유전적 특성은 환경 변화에 대한 생태계의 대응 능력에 기여할 수 있습니다."),
        ("한 지역에 외래종이 들어와 토종 생물과 먹이·서식지를 경쟁하면 발생할 수 있는 문제는?",
         ["토종 생물의 개체 수가 감소할 수 있다",
          "모든 종의 개체 수가 반드시 증가한다",
          "먹이 관계가 사라진다",
          "기후가 즉시 일정해진다"], 0,
         "외래종이 자원을 차지하거나 포식·질병 등을 일으키면 토종 생물에 영향을 줄 수 있습니다."),
        ("개체군의 크기를 제한할 수 있는 요인으로 가장 알맞은 것은?",
         ["먹이와 서식 공간의 부족", "항상 일정한 유전자 수",
          "모든 개체의 동일한 나이", "계절과 무관한 환경"], 0,
         "먹이, 공간, 질병, 포식 등은 개체군 크기에 영향을 주는 요인입니다."),
        ("생물 농축이 일어날 때 먹이사슬의 상위 포식자에서 특정 오염 물질의 농도가 높아질 수 있는 이유는?",
         ["오염 물질이 먹이 관계를 따라 축적될 수 있기 때문에",
          "포식자는 물을 마시지 않기 때문에",
          "생산자는 항상 오염 물질을 만들기 때문에",
          "에너지가 물질로 변하기 때문에"], 0,
         "분해되기 어렵거나 배출이 느린 오염 물질은 먹이를 통해 전달되고 체내에 축적될 수 있습니다."),
        ("서식지 단편화가 생물에게 미칠 수 있는 영향은?",
         ["개체군 사이의 이동과 유전자 교류가 줄어들 수 있다",
          "모든 생물의 이동이 쉬워진다",
          "생물 다양성이 항상 증가한다",
          "먹이사슬이 완전히 없어지지 않는다"], 0,
         "서식지가 작은 조각으로 나뉘면 생물의 이동과 개체군 사이의 유전자 교류가 제한될 수 있습니다."),
    ],
    "초희귀": [
        ("유전적 다양성이 낮은 작은 개체군에서 특히 우려되는 현상은?",
         ["유전적 부동과 근친 교배의 영향이 커질 수 있다",
          "돌연변이가 절대로 일어나지 않는다",
          "모든 개체가 동일한 환경 적응력을 가진다",
          "자연선택이 불가능해진다"], 0,
         "작은 개체군에서는 우연한 유전자 빈도 변화와 근친 교배의 영향이 상대적으로 커질 수 있습니다."),
        ("기후 변화로 서식 가능 지역이 이동할 때 이동 능력이 낮은 생물이 겪을 수 있는 위험은?",
         ["적합한 서식지를 따라 이동하지 못할 수 있다",
          "모든 개체가 즉시 새로운 종이 된다",
          "먹이가 자동으로 증가한다",
          "유전 정보가 모두 사라진다"], 0,
         "기후대가 이동해도 생물이 새로운 적합 서식지에 도달하지 못하면 생존이 어려워질 수 있습니다."),
        ("생태계에서 핵심종이 사라졌을 때 나타날 수 있는 결과는?",
         ["먹이 관계와 생태계 구조가 크게 변할 수 있다",
          "다른 모든 종이 반드시 번성한다",
          "물질 순환이 즉시 멈춘다",
          "생물 다양성이 항상 높아진다"], 0,
         "핵심종은 생태계 구조에 큰 영향을 주므로 사라지면 여러 종의 관계가 달라질 수 있습니다."),
        ("멸종 위기 생물의 보전 계획에서 서식지 보전이 중요한 이유는?",
         ["먹이·번식 장소와 생태적 관계를 함께 보호할 수 있기 때문에",
          "생물의 모든 질병을 없애기 때문에",
          "모든 종의 유전자를 같게 만들기 때문에",
          "생태계의 계절 변화를 없애기 때문에"], 0,
         "서식지는 먹이, 번식, 은신처 등 생존에 필요한 조건을 제공하므로 보전의 핵심입니다."),
    ],
    "전설": [
        ("어떤 개체군에서 특정 유전 형질의 빈도가 여러 세대에 걸쳐 달라질 수 있는 요인을 가장 정확히 묶은 것은?",
         ["자연선택, 돌연변이, 유전자 흐름, 유전적 부동",
          "개체의 의지만으로 생기는 변화",
          "먹이의 양만으로 결정되는 변화",
          "모든 개체에서 동일하게 일어나는 변화"], 0,
         "진화는 자연선택뿐 아니라 돌연변이, 유전자 흐름, 유전적 부동 등 여러 요인의 영향을 받습니다."),
        ("서식지 복원 사업의 효과를 평가할 때 가장 신뢰할 만한 접근은?",
         ["복원 전후의 생물·환경 자료를 비교하고 대조 지역도 함께 조사한다",
          "복원 직후 한 종만 한 번 관찰한다",
          "사진 한 장만으로 모든 효과를 판단한다",
          "조사 결과와 관계없이 성공으로 결론 내린다"], 0,
         "전후 자료와 비교 가능한 대조 지역을 함께 살펴보면 자연적인 변동과 사업 효과를 구분하는 데 도움이 됩니다."),
        ("작은 개체군의 보전에서 개체 수 증가와 함께 유전적 다양성을 고려해야 하는 이유는?",
         ["유전적 다양성이 낮으면 환경 변화와 질병에 취약해질 수 있기 때문에",
          "유전적 다양성이 있으면 진화가 멈추기 때문에",
          "개체 수가 늘면 유전자는 모두 같아지기 때문에",
          "유전적 다양성은 생존과 관계가 없기 때문에"], 0,
         "유전적 다양성은 개체군이 환경 변화와 질병에 대응할 수 있는 잠재력과 관련이 있습니다."),
        ("먹이그물에서 한 종의 감소가 다른 여러 종에 영향을 줄 수 있는 가장 적절한 이유는?",
         ["여러 종이 포식·먹이·경쟁 관계로 연결되어 있기 때문에",
          "모든 종이 같은 유전자를 갖기 때문에",
          "생태계에는 한 가지 먹이 관계만 있기 때문에",
          "에너지가 생태계에서 순환하지 않기 때문에"], 0,
         "먹이그물은 여러 먹이 관계가 연결된 구조이므로 한 종의 변화가 다른 종에 연쇄적으로 영향을 줄 수 있습니다."),
    ],
}

RARITY_ORDER = ["일반", "고급", "희귀", "초희귀", "전설"]

# -------------------- 세션 상태 --------------------

def init_state():
    defaults = {
        "terrain": "숲",
        "page": "🌲 탐험하기",
        "discovered": {},
        "xp": 0,
        "total_found": 0,
        "total_encounters": 0,
        "total_missed": 0,
        "current_creature": None,
        "current_question": None,
        "quiz_options": None,
        "quiz_answer": None,
        "quiz_submitted": False,
        "last_result": None,
        "encounter_id": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# -------------------- 사진 가져오기 --------------------

@st.cache_data(ttl=86400, show_spinner=False)
def get_creature_image(korean_name, english_name):
    """
    한국어·영어 위키백과와 Wikimedia Commons를 순서대로 검색.
    찾지 못하면 None을 반환한다.
    """
    headers = {"User-Agent": "BioHunterEducationalApp/1.0"}
    names = [korean_name]
    if english_name and english_name != korean_name:
        names.append(english_name)

    # 1. 한국어 및 영어 위키백과 대표 사진
    for lang, name in [
        ("ko", korean_name),
        ("en", english_name),
    ]:
        if not name:
            continue
        try:
            url = (
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                + quote(name.replace(" ", "_"), safe="")
            )
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                image_url = (
                    data.get("thumbnail", {}).get("source")
                    or data.get("originalimage", {}).get("source")
                )
                if image_url:
                    return image_url
        except (requests.RequestException, ValueError):
            pass

    # 2. Wikimedia Commons 이미지 검색
    for name in names:
        try:
            response = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": f'filetype:bitmap "{name}"',
                    "gsrnamespace": 6,
                    "gsrlimit": 6,
                    "prop": "imageinfo",
                    "iiprop": "url|mime",
                    "iiurlwidth": 700,
                    "format": "json",
                },
                headers=headers,
                timeout=7,
            )
            if response.status_code == 200:
                pages = response.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    image_info = page.get("imageinfo", [{}])[0]
                    mime = image_info.get("mime", "")
                    if mime.startswith("image/"):
                        return (
                            image_info.get("thumburl")
                            or image_info.get("url")
                        )
        except (requests.RequestException, ValueError, IndexError):
            pass

    return None

def show_creature_image(creature, width=300):
    image_url = get_creature_image(
        creature["name"], creature["english"]
    )
    if image_url:
        try:
            st.image(image_url, width=width)
        except Exception:
            st.markdown(
                f"<div style='font-size:90px;text-align:center;'>"
                f"{creature['emoji']}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div style='font-size:90px;text-align:center;'>"
            f"{creature['emoji']}</div>",
            unsafe_allow_html=True,
        )
        st.caption("사진을 찾지 못해 대표 아이콘을 표시했어요.")

# -------------------- 게임 로직 --------------------

def get_terrain_species(terrain):
    allowed = TERRAINS[terrain]["habitats"]
    return [
        creature for creature in SPECIES
        if any(habitat in allowed for habitat in creature["habitat"])
    ]

def choose_rarity():
    # 희귀도 확률은 지형이나 발견 수와 무관하게 동일하게 유지
    rarities = list(RARITY_INFO.keys())
    weights = [RARITY_INFO[r]["weight"] for r in rarities]
    return random.choices(rarities, weights=weights, k=1)[0]

def choose_creature(terrain):
    candidates = get_terrain_species(terrain)
    if not candidates:
        return random.choice(SPECIES)

    # 먼저 희귀도를 독립적으로 뽑고, 해당 희귀도의 생물을 선택
    rarity = choose_rarity()
    same_rarity = [c for c in candidates if c["rarity"] == rarity]

    # 현재 지형에 해당 희귀도 생물이 없다면 지형 내 가능한 희귀도 중 선택
    if not same_rarity:
        available_rarities = list({c["rarity"] for c in candidates})
        rarity = random.choice(available_rarities)
        same_rarity = [c for c in candidates if c["rarity"] == rarity]

    # 중복 발견 생물은 약간 더 자주 등장하도록 가중치 부여
    # 새 생물도 등장할 수 있도록 가중치를 과도하게 높이지 않는다.
    weights = [
        1.8 if c["name"] in st.session_state.discovered else 1.0
        for c in same_rarity
    ]
    return random.choices(same_rarity, weights=weights, k=1)[0]

def choose_question(creature):
    rarity = creature["rarity"]
    question = random.choice(QUIZZES[rarity])
    text, options, answer, explanation = question
    shuffled = list(enumerate(options))
    random.shuffle(shuffled)

    correct_new_index = next(
        i for i, original_index in enumerate(
            [original_index for original_index, _ in shuffled]
        )
        if original_index == answer
    )
    return {
        "text": text,
        "options": [option for _, option in shuffled],
        "answer": correct_new_index,
        "explanation": explanation,
        "rarity": rarity,
    }

def start_exploration():
    creature = choose_creature(st.session_state.terrain)
    st.session_state.current_creature = creature
    st.session_state.current_question = choose_question(creature)
    st.session_state.quiz_options = None
    st.session_state.quiz_answer = None
    st.session_state.quiz_submitted = False
    st.session_state.last_result = None
    st.session_state.encounter_id += 1
    st.session_state.total_encounters += 1

def resolve_answer(selected_answer):
    creature = st.session_state.current_creature
    question = st.session_state.current_question

    if not creature or not question:
        return

    if selected_answer is None:
        st.warning("답을 하나 선택해 줘.")
        return

    st.session_state.quiz_submitted = True
    st.session_state.quiz_answer = selected_answer

    if selected_answer == question["answer"]:
        name = creature["name"]
        rarity = creature["rarity"]
        st.session_state.xp += RARITY_INFO[rarity]["xp"]

        if name in st.session_state.discovered:
            st.session_state.discovered[name]["count"] += 1
            st.session_state.xp += 3
            st.session_state.last_result = "duplicate"
        else:
            st.session_state.discovered[name] = {
                "count": 1,
                "first_terrain": st.session_state.terrain,
            }
            st.session_state.total_found += 1
            st.session_state.last_result = "new"
    else:
        st.session_state.total_missed += 1
        st.session_state.last_result = "missed"

# -------------------- 사이드바 --------------------

with st.sidebar:
    st.title("🌿 바이오 헌터")
    st.caption("탐험하고, 배우고, 수집하자!")

    st.selectbox(
        "탐험할 지형",
        list(TERRAINS.keys()),
        key="terrain",
    )

    st.divider()
    st.metric("🧬 발견한 종류", f"{len(st.session_state.discovered)} / {len(SPECIES)}")
    st.metric("⭐ 경험치", st.session_state.xp)
    st.metric("🔎 탐험 횟수", st.session_state.total_encounters)

    st.divider()
    pages = [
        "🌲 탐험하기",
        "📖 생물 도감",
        "🏆 업적",
        "⚙️ 설정",
    ]
    st.radio("메뉴", pages, key="page")

# -------------------- 공통 헤더 --------------------

st.title("🌿 바이오 헌터")
st.caption("생명과학 지식을 활용해 자연 속 생물을 발견해 보세요.")

# =========================================================
# 탐험하기
# =========================================================

if st.session_state.page == "🌲 탐험하기":
    terrain = st.session_state.terrain
    terrain_info = TERRAINS[terrain]

    st.header(f"{terrain_info['emoji']} {terrain} 탐험")
    st.write(terrain_info["description"] + "을 탐험해 보자.")

    col1, col2, col3 = st.columns(3)
    col1.metric("발견한 생물", len(st.session_state.discovered))
    col2.metric("획득 경험치", st.session_state.xp)
    col3.metric("놓친 생물", st.session_state.total_missed)

    if st.session_state.current_creature is None:
        st.info("탐험을 시작하면 야생 생물과 생명과학 퀴즈가 나타나요.")
        if st.button("🔍 탐험 시작!", type="primary", use_container_width=True):
            start_exploration()
            st.rerun()
    else:
        creature = st.session_state.current_creature
        question = st.session_state.current_question

        st.divider()
        st.subheader("야생 생물을 발견했다!")
        st.write(
            f"{RARITY_INFO[creature['rarity']]['emoji']} "
            f"**{creature['rarity']} 생물**이 나타났어!"
        )

        left, right = st.columns([1, 1.3])
        with left:
            show_creature_image(creature, width=300)
        with right:
            st.markdown(f"### {creature['emoji']} 생물 정보")
            st.write(f"**분류:** {creature['category']}")
            st.write(f"**서식지:** {', '.join(creature['habitat'])}")
            st.write(f"**희귀도:** {creature['rarity']}")
            st.write("정답을 맞히면 생물을 획득할 수 있어!")

        st.divider()
        st.subheader("🧠 생명과학 퀴즈")
        st.write(f"**{question['text']}**")

        answer_key = f"answer_{st.session_state.encounter_id}"
        if not st.session_state.quiz_submitted:
            selected = st.radio(
                "정답을 선택해 줘.",
                question["options"],
                index=None,
                key=answer_key,
            )

            if st.button("정답 제출", type="primary", use_container_width=True):
                if selected is None:
                    st.warning("먼저 답을 선택해 줘.")
                else:
                    selected_index = question["options"].index(selected)
                    resolve_answer(selected_index)
                    st.rerun()
        else:
            result = st.session_state.last_result
            selected_index = st.session_state.quiz_answer

            if result in ("new", "duplicate"):
                st.success("🎉 정답! 생물을 획득했어!")
                if result == "new":
                    st.balloons()
                    st.markdown(f"## 🆕 새로운 생물: {creature['name']}")
                else:
                    st.markdown(f"## 🔁 {creature['name']} 중복 발견!")
                    st.write("이미 발견한 생물이지만 경험치를 추가로 얻었어.")
                st.write(
                    f"**획득 경험치:** +{RARITY_INFO[creature['rarity']]['xp']}"
                    + (" (+3 중복 보너스)" if result == "duplicate" else "")
                )
                st.write(f"**영어 이름:** {creature['english']}")
                st.write(f"**특징:** {creature['description']}")
            else:
                st.error(f"💨 아쉽다! {creature['name']}을(를) 놓쳤어.")
                st.write("다음 탐험에서 다시 도전해 보자!")

            st.info(
                f"정답: **{question['options'][question['answer']]}**\n\n"
                f"{question['explanation']}"
            )

            if st.button("다음 탐험으로!", type="primary", use_container_width=True):
                start_exploration()
                st.rerun()

# =========================================================
# 생물 도감
# =========================================================

elif st.session_state.page == "📖 생물 도감":
    st.header("📖 생물 도감")
    found_count = len(st.session_state.discovered)
    st.progress(found_count / max(len(SPECIES), 1))
    st.write(f"**수집 진행도: {found_count} / {len(SPECIES)}종**")

    terrain_tab_names = list(TERRAINS.keys())
    tabs = st.tabs(terrain_tab_names)

    for tab, terrain in zip(tabs, terrain_tab_names):
        with tab:
            terrain_species = get_terrain_species(terrain)
            category_options = ["전체"] + sorted(
                {c["category"] for c in terrain_species}
            )
            chosen_category = st.selectbox(
                "분류 선택",
                category_options,
                key=f"category_{terrain}",
            )

            rarity_options = ["전체"] + RARITY_ORDER
            chosen_rarity = st.selectbox(
                "희귀도 선택",
                rarity_options,
                key=f"rarity_{terrain}",
            )

            visible = []
            for creature in terrain_species:
                if chosen_category != "전체" and creature["category"] != chosen_category:
                    continue
                if chosen_rarity != "전체" and creature["rarity"] != chosen_rarity:
                    continue
                visible.append(creature)

            st.caption(f"이 지형에서 확인할 수 있는 생물: {len(visible)}종")

            if not visible:
                st.info("선택한 조건에 해당하는 생물이 없어.")
            else:
                cols_per_row = 3
                for start in range(0, len(visible), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for col, creature in zip(
                        cols, visible[start:start + cols_per_row]
                    ):
                        with col:
                            name = creature["name"]
                            found = name in st.session_state.discovered
                            st.markdown('<div class="creature-box">', unsafe_allow_html=True)

                            if found:
                                show_creature_image(creature, width=180)
                                st.markdown(f"### {creature['emoji']} {name}")
                                st.caption(creature["english"])
                                st.write(
                                    f"{RARITY_INFO[creature['rarity']]['emoji']} "
                                    f"{creature['rarity']} · {creature['category']}"
                                )
                                st.write(creature["description"])
                                st.caption(
                                    f"발견 횟수: "
                                    f"{st.session_state.discovered[name]['count']}회"
                                )
                            else:
                                st.markdown(
                                    "<div style='font-size:70px;text-align:center;'>❓</div>",
                                    unsafe_allow_html=True,
                                )
                                st.markdown("### 미발견 생물")
                                st.write("탐험에서 퀴즈를 맞혀 발견해 보자!")
                                st.caption(
                                    f"{RARITY_INFO[creature['rarity']]['emoji']} "
                                    f"{creature['rarity']} · {creature['category']}"
                                )

                            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 업적
# =========================================================

elif st.session_state.page == "🏆 업적":
    st.header("🏆 탐험 업적")

    found_count = len(st.session_state.discovered)
    milestones = [
        (1, "첫 발견", "처음으로 생물을 도감에 등록하기"),
        (5, "자연 탐험가", "5종의 생물 발견하기"),
        (10, "생물 수집가", "10종의 생물 발견하기"),
        (25, "생태계 전문가", "25종의 생물 발견하기"),
        (50, "바이오 마스터", "50종의 생물 발견하기"),
        (100, "전설의 탐험가", "100종의 생물 발견하기"),
    ]

    for target, title, description in milestones:
        if found_count >= target:
            st.success(f"🏅 **{title}** — {description}")
        else:
            st.write(f"🔒 **{title}** — {description} ({found_count}/{target})")

    st.divider()
    st.subheader("희귀 생물 업적")

    found_rarities = {
        SPECIES_BY_NAME[name]["rarity"]
        for name in st.session_state.discovered
        if name in SPECIES_BY_NAME
    }

    for rarity in RARITY_ORDER:
        if rarity in found_rarities:
            st.success(f"{RARITY_INFO[rarity]['emoji']} {rarity} 생물 발견!")
        else:
            st.write(f"🔒 {RARITY_INFO[rarity]['emoji']} {rarity} 생물 발견하기")

    st.divider()
    st.subheader("탐험 기록")
    a, b, c = st.columns(3)
    a.metric("탐험 횟수", st.session_state.total_encounters)
    b.metric("획득 종류", found_count)
    c.metric("놓친 횟수", st.session_state.total_missed)

# =========================================================
# 설정
# =========================================================

elif st.session_state.page == "⚙️ 설정":
    st.header("⚙️ 설정")
    st.write("현재 세션의 탐험 기록을 확인하고 초기화할 수 있어.")
    st.caption("이 앱은 수집 기록을 영구 저장하지 않아. 앱 세션이 초기화되면 기록도 사라져.")

    st.metric("총 생물 종류", len(SPECIES))
    st.metric("발견한 종류", len(st.session_state.discovered))
    st.metric("획득 경험치", st.session_state.xp)
    st.metric("놓친 생물", st.session_state.total_missed)

    st.divider()
    st.subheader("기록 초기화")

    confirm_reset = st.checkbox(
        "현재 세션의 도감과 경험치를 초기화하는 것에 동의해.",
        key="confirm_reset",
    )

    if st.button("🗑️ 게임 기록 초기화", disabled=not confirm_reset):
        for key in [
            "discovered", "xp", "total_found", "total_encounters",
            "total_missed", "current_creature", "current_question",
            "quiz_options", "quiz_answer", "quiz_submitted",
            "last_result", "encounter_id",
        ]:
            if key in st.session_state:
                del st.session_state[key]

        init_state()
        st.session_state.page = "⚙️ 설정"
        st.success("현재 게임 기록을 초기화했어.")
        st.rerun()

st.divider()
st.caption(
    "🌱 바이오 헌터 | 생물과 생명과학을 배우며 자연을 탐험하는 게임"
)
