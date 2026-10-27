
import random
import requests
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="바이오 헌터",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 화면 디자인
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background:
        radial-gradient(ellipse at top left, #e7f5d9 0%, transparent 40%),
        linear-gradient(180deg, #f6f8eb 0%, #edf4e4 100%);
}
h1, h2, h3 {
    font-family: 'Jua', sans-serif !important;
    color: #244b35;
}
.hero {
    background: linear-gradient(135deg, #244b35, #4e8053);
    color: white;
    border-radius: 24px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px #244b3522;
}
.hero h1 {
    color: white !important;
    font-size: 42px;
    margin: 0;
}
.hero p {
    font-size: 16px;
    color: #edf8e8;
    margin-bottom: 0;
}
.panel {
    background: rgba(255,255,255,0.9);
    border: 1px solid #dce8d4;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 14px;
}
.creature {
    background: #ffffff;
    border: 1px solid #dce8d4;
    border-radius: 20px;
    padding: 15px;
    margin-bottom: 14px;
}
.tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 30px;
    background: #e7f2df;
    color: #315f3e;
    font-size: 12px;
    font-weight: 700;
    margin: 2px;
}
.small-muted {
    color: #667565;
    font-size: 13px;
}
div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 42px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce8d4;
    border-radius: 16px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 생물 데이터
# 형식: 이름 | 영어 이름 | 분류 | 서식지 | 희귀도 | 설명
# =========================================================
RAW_SPECIES = """
참개구리|Black-spotted pond frog|양서류|연못,습지|일반|논과 연못 주변에서 볼 수 있는 개구리
청개구리|Japanese tree frog|양서류|숲,습지|고급|나뭇잎이나 풀 위에서 생활하는 작은 개구리
두꺼비|Asian common toad|양서류|숲,습지|고급|피부에 독성 물질을 분비하는 양서류
도롱뇽|Korean salamander|양서류|숲,계곡|희귀|습한 곳에서 생활하는 양서류
무당개구리|Oriental fire-bellied toad|양서류|계곡,습지|희귀|배 부분의 화려한 무늬가 특징
맹꽁이|Korean narrow-mouthed toad|양서류|습지|초희귀|땅속에서 생활하는 시간이 긴 양서류
수원청개구리|Suwon tree frog|양서류|논,습지|전설|우리나라에서 보호가 중요한 희귀 양서류
산개구리|Brown frog|양서류|숲,계곡|일반|산지의 물가에서 관찰할 수 있는 개구리
아무르산개구리|Amur brown frog|양서류|숲,계곡|고급|산지와 숲 주변에서 살아가는 개구리
황소개구리|American bullfrog|양서류|연못,습지|일반|몸집이 크고 식욕이 왕성한 개구리
고라니|Water deer|포유류|숲,초원|일반|우리나라에서 흔히 관찰되는 사슴과 동물
너구리|Raccoon dog|포유류|숲|일반|야행성이며 다양한 먹이를 먹는 동물
오소리|Asian badger|포유류|숲|고급|땅을 파서 굴을 만드는 포유류
멧돼지|Wild boar|포유류|숲|일반|잡식성이며 후각이 발달한 동물
다람쥐|Siberian chipmunk|포유류|숲|일반|볼주머니에 먹이를 저장하는 동물
청설모|Red squirrel|포유류|숲|일반|나무 위에서 생활하는 다람쥐류
고슴도치|Amur hedgehog|포유류|숲,초원|고급|몸에 가시가 있는 작은 포유류
족제비|Least weasel|포유류|숲,초원|고급|몸이 길고 작은 동물을 사냥하는 포유류
수달|Eurasian otter|포유류|강,습지|희귀|물속 생활에 적응한 포유류
삵|Leopard cat|포유류|숲|희귀|우리나라에 사는 야생 고양잇과 동물
반달가슴곰|Asiatic black bear|포유류|숲,산|초희귀|가슴에 반달 모양 무늬가 나타나는 곰
산양|Long-tailed goral|포유류|산|초희귀|바위가 많은 산악 지대에 적응한 동물
여우|Red fox|포유류|숲,초원|희귀|청각과 후각이 발달한 포유류
토끼|European rabbit|포유류|초원|일반|초식성이며 번식 속도가 빠른 포유류
고라니새끼|Young water deer|포유류|숲,초원|고급|몸집이 작은 어린 고라니
박쥐|Bat|포유류|숲,동굴|고급|날개를 가진 포유류로 초음파를 이용하는 종도 있음
큰수염박쥐|Greater mouse-eared bat|포유류|숲,동굴|희귀|어두운 곳에서 활동하는 박쥐류
하늘다람쥐|Siberian flying squirrel|포유류|숲|초희귀|피부막을 이용해 나무 사이를 활공하는 포유류
늑대|Wolf|포유류|숲,초원|전설|무리 생활과 협동 사냥으로 알려진 포유류
호랑이|Tiger|포유류|숲|전설|강한 포식자로 생태계 먹이사슬의 상위에 위치
참새|Eurasian tree sparrow|조류|도시,숲|일반|도시 주변에서도 흔히 볼 수 있는 작은 새
까치|Oriental magpie|조류|도시,숲|일반|검고 흰 깃털과 긴 꼬리가 특징
까마귀|Large-billed crow|조류|도시,숲|일반|학습 능력이 뛰어난 새
박새|Japanese tit|조류|숲|일반|나무 사이를 돌아다니며 곤충을 먹는 작은 새
직박구리|Brown-eared bulbul|조류|도시,숲|일반|도시와 정원에서 자주 관찰되는 새
딱따구리|Great spotted woodpecker|조류|숲|고급|나무를 두드려 먹이를 찾는 새
물총새|Common kingfisher|조류|강,습지|희귀|물속의 작은 물고기를 사냥하는 새
왜가리|Grey heron|조류|강,습지|고급|긴 다리와 부리를 이용해 물고기를 잡는 새
백로|Little egret|조류|강,습지|고급|흰 깃털과 긴 다리가 특징인 물가의 새
청둥오리|Mallard|조류|강,습지|일반|연못과 하천에서 관찰되는 오리
원앙|Mandarin duck|조류|숲,강|희귀|수컷의 화려한 깃털이 특징
수리부엉이|Eurasian eagle-owl|조류|숲,산|초희귀|큰 눈과 귀깃이 특징인 야행성 맹금류
소쩍새|Oriental scops owl|조류|숲|희귀|밤에 활동하며 특유의 울음소리를 내는 새
황조롱이|Common kestrel|조류|도시,초원|희귀|공중에서 정지 비행하며 먹이를 찾는 맹금류
독수리|Cinereous vulture|조류|산,초원|초희귀|죽은 동물을 먹어 생태계의 청소부 역할을 함
두루미|Red-crowned crane|조류|습지|전설|습지 보전의 상징으로 알려진 대형 조류
저어새|Black-faced spoonbill|조류|습지|전설|주걱 모양 부리로 물속 먹이를 찾는 새
제비|Barn swallow|조류|도시,초원|일반|날아다니는 곤충을 잡아먹는 새
꿩|Common pheasant|조류|숲,초원|일반|수컷의 화려한 깃털이 특징
기러기|Wild goose|조류|습지|고급|무리를 지어 이동하는 물새
펭귄|Penguin|조류|바다|희귀|날개가 물속에서 헤엄치기에 적합하게 발달한 새
잉어|Common carp|어류|강,연못|일반|민물에서 살아가는 큰 물고기
붕어|Crucian carp|어류|연못,강|일반|연못과 하천에서 흔히 볼 수 있는 물고기
피라미|Pale chub|어류|강,계곡|일반|물살이 있는 민물에서 관찰되는 작은 물고기
미꾸라지|Oriental weather loach|어류|논,습지|일반|진흙 속에서도 생활할 수 있는 물고기
메기|Amur catfish|어류|강,연못|고급|수염으로 주변을 탐색하는 민물고기
쏘가리|Mandarin fish|어류|강|희귀|민물 생태계의 포식성 어류
은어|Ayu|어류|강|희귀|성장하면서 먹이와 서식 환경이 달라지는 물고기
연어|Salmon|어류|강,바다|희귀|일부 종은 번식을 위해 바다에서 강으로 이동
장어|Japanese eel|어류|강,바다|초희귀|성장 단계에 따라 생활 환경이 달라지는 어류
철갑상어|Sturgeon|어류|강,바다|전설|오래된 계통의 특징을 가진 대형 어류
금붕어|Goldfish|어류|연못|일반|사람이 기르도록 품종 개량된 물고기
가물치|Northern snakehead|어류|연못,습지|고급|공기 중 산소도 이용할 수 있는 물고기
송사리|Japanese rice fish|어류|논,습지|일반|작고 얕은 물에서 생활하는 물고기
복어|Pufferfish|어류|바다|희귀|위협을 받으면 몸을 부풀리는 종이 있음
흰동가리|Clownfish|어류|바다|희귀|말미잘과 상호작용하며 살아가는 물고기
상어|Shark|어류|바다|초희귀|여러 종류가 있으며 해양 먹이사슬에서 중요한 역할
해마|Seahorse|어류|바다|초희귀|수컷이 알을 품는 독특한 번식 방식으로 알려짐
바다거북|Sea turtle|파충류|바다|초희귀|바다에서 생활하고 알은 육지에 낳는 파충류
남생이|Reeves's turtle|파충류|연못,강|희귀|민물에서 생활하는 거북
자라|Chinese softshell turtle|파충류|강,연못|고급|딱딱한 등딱지 대신 부드러운 피부가 특징
살모사|Viper|파충류|숲,초원|희귀|독을 가진 뱀으로 야생에서 주의가 필요
구렁이|Rat snake|파충류|숲,초원|희귀|큰 몸집의 뱀으로 설치류 등을 먹음
도마뱀|Lizard|파충류|숲,초원|일반|비늘로 덮인 피부를 가진 파충류
장지뱀|Grass lizard|파충류|초원|고급|햇볕이 잘 드는 곳에서 관찰되는 작은 파충류
이구아나|Iguana|파충류|숲|희귀|일부 종은 식물을 주로 먹는 파충류
악어|Crocodile|파충류|습지,강|전설|물속 생활에 적응한 대형 파충류
카멜레온|Chameleon|파충류|숲|초희귀|눈을 독립적으로 움직일 수 있는 종이 있음
꿀벌|Honey bee|곤충|숲,초원|일반|꽃가루받이를 돕는 사회성 곤충
호랑나비|Asian swallowtail|곤충|숲,초원|일반|애벌레와 성충의 모습이 크게 다른 곤충
장수풍뎅이|Japanese rhinoceros beetle|곤충|숲|고급|수컷의 큰 뿔이 특징
사슴벌레|Stag beetle|곤충|숲|고급|큰 턱을 가진 딱정벌레
무당벌레|Ladybug|곤충|숲,초원|일반|진딧물 등을 먹는 종이 많음
잠자리|Dragonfly|곤충|연못,습지|일반|날개가 발달하고 비행 능력이 뛰어난 곤충
반딧불이|Firefly|곤충|습지,숲|희귀|빛을 내는 발광 기관을 가진 곤충
사마귀|Praying mantis|곤충|초원,숲|일반|앞다리를 이용해 먹이를 잡는 포식성 곤충
메뚜기|Grasshopper|곤충|초원|일반|뒷다리가 발달해 멀리 뛸 수 있는 곤충
매미|Cicada|곤충|숲,도시|일반|수컷이 소리를 내어 짝을 찾는 곤충
개미|Ant|곤충|숲,도시|일반|협동 생활을 하는 사회성 곤충
왕잠자리|Common green darner|곤충|연못,습지|고급|비행 능력이 뛰어난 대형 잠자리
길앞잡이|Tiger beetle|곤충|초원|희귀|빠르게 달리며 작은 동물을 사냥하는 딱정벌레
물방개|Predaceous diving beetle|곤충|연못,습지|고급|물속에서 사냥하는 수생 딱정벌레
대벌레|Stick insect|곤충|숲|희귀|나뭇가지처럼 보이는 몸으로 위장하는 곤충
누에나방|Silkworm moth|곤충|숲|고급|누에의 성충으로 양잠과 관련이 있음
장수하늘소|Jewel beetle|곤충|숲|전설|보전 가치가 높은 대형 딱정벌레류
민들레|Dandelion|식물|초원,도시|일반|바람을 이용해 씨앗을 퍼뜨리는 식물
소나무|Korean red pine|식물|숲,산|일반|바늘 모양 잎을 가진 상록 침엽수
은행나무|Ginkgo|식물|도시,숲|고급|오래된 식물 계통으로 알려진 나무
벚나무|Cherry tree|식물|숲,도시|일반|봄에 꽃이 피는 나무
해바라기|Sunflower|식물|초원|일반|큰 꽃과 씨앗이 특징인 식물
연꽃|Sacred lotus|식물|연못,습지|고급|물 위로 잎과 꽃을 펼치는 수생식물
끈끈이주걱|Sundew|식물|습지|희귀|끈끈한 잎으로 작은 곤충을 잡는 식충식물
파리지옥|Venus flytrap|식물|습지|희귀|자극에 반응해 잎을 닫는 식충식물
은행나무새싹|Ginkgo seedling|식물|숲,도시|일반|자라면서 부채 모양 잎을 만드는 어린 나무
주목|Japanese yew|식물|산,숲|초희귀|독성 성분을 가진 부분이 있어 주의가 필요한 나무
"""

RARITY_INFO = {
    "일반": {"weight": 58, "xp": 10, "color": "#8b9b87", "emoji": "🍃"},
    "고급": {"weight": 25, "xp": 20, "color": "#439b64", "emoji": "🌿"},
    "희귀": {"weight": 12, "xp": 40, "color": "#4488d6", "emoji": "💎"},
    "초희귀": {"weight": 4, "xp": 80, "color": "#a66ad5", "emoji": "✨"},
    "전설": {"weight": 1, "xp": 150, "color": "#d59a26", "emoji": "👑"},
}

SPECIES = []
for line in RAW_SPECIES.strip().splitlines():
    parts = [x.strip() for x in line.split("|")]
    if len(parts) == 6:
        name, english, category, habitat, rarity, description = parts
        SPECIES.append({
            "name": name,
            "english": english,
            "category": category,
            "habitat": habitat,
            "rarity": rarity,
            "description": description,
        })

# =========================================================
# 퀴즈 데이터
# =========================================================
QUIZZES = {
    "쉬움": [
        ("식물의 광합성에 주로 필요한 에너지원은?", ["달빛", "햇빛", "소리", "바람"], 1,
         "광합성은 빛에너지를 이용해 유기물을 만드는 과정이야."),
        ("생물의 유전 정보를 주로 저장하는 물질은?", ["DNA", "지방", "물", "녹말"], 0,
         "DNA에는 생물의 유전 정보가 저장되어 있어."),
        ("다음 중 포유류는?", ["개구리", "참새", "고라니", "잉어"], 2,
         "고라니는 새끼를 낳고 젖을 먹여 기르는 포유류야."),
        ("곤충의 다리는 보통 몇 쌍일까?", ["1쌍", "2쌍", "3쌍", "4쌍"], 2,
         "곤충의 다리는 세 쌍, 즉 여섯 개야."),
        ("먹이사슬에서 식물의 역할은?", ["생산자", "분해자", "최상위 포식자", "기생자"], 0,
         "식물은 광합성으로 유기물을 만들어 생산자 역할을 해."),
        ("물고기가 주로 호흡하는 기관은?", ["폐", "아가미", "피부만", "기관"], 1,
         "대부분의 물고기는 아가미로 물속의 산소를 얻어."),
        ("개구리는 어느 분류에 속할까?", ["파충류", "양서류", "포유류", "조류"], 1,
         "개구리는 양서류에 속해."),
        ("꽃가루받이를 돕는 곤충은?", ["꿀벌", "모기 유충", "벼룩", "이"], 0,
         "꿀벌은 꽃 사이를 오가며 꽃가루받이를 도와."),
        ("생태계에서 죽은 생물을 분해하는 생물의 예는?", ["버섯", "독수리", "사슴", "나비"], 0,
         "곰팡이와 많은 세균은 유기물을 분해해."),
        ("다음 중 파충류는?", ["도마뱀", "수달", "비둘기", "도롱뇽"], 0,
         "도마뱀은 비늘이 있는 파충류야."),
        ("식물의 뿌리가 주로 하는 일은?", ["빛 흡수", "물과 무기질 흡수", "꽃가루 만들기", "씨앗 이동"], 1,
         "뿌리는 물과 무기질을 흡수하고 식물을 지지해."),
        ("생물이 살아가는 장소를 무엇이라고 할까?", ["서식지", "염색체", "세포막", "효소"], 0,
         "서식지는 생물이 살아가는 장소를 뜻해."),
    ],
    "보통": [
        ("세포에서 에너지를 만드는 데 중요한 역할을 하는 세포 소기관은?", ["리보솜", "미토콘드리아", "핵", "골지체"], 1,
         "미토콘드리아는 세포 호흡으로 ATP를 만드는 데 중요한 역할을 해."),
        ("효소의 일반적인 특징으로 알맞은 것은?", ["반응 후 모두 소모된다", "특정 반응을 촉진한다", "모든 물질과 똑같이 반응한다", "항상 고온에서만 작용한다"], 1,
         "효소는 특정 반응을 빠르게 하며 반응 후에도 재사용될 수 있어."),
        ("생태계의 생물 다양성이 높을 때 기대할 수 있는 점은?", ["모든 생물이 사라진다", "생태계가 변화에 대응할 가능성이 커진다", "먹이 관계가 사라진다", "에너지 흐름이 멈춘다"], 1,
         "다양한 생물과 상호작용은 생태계의 안정성에 도움을 줄 수 있어."),
        ("DNA의 염기 네 가지에 해당하지 않는 것은?", ["아데닌", "티민", "우라실", "구아닌"], 2,
         "DNA에는 A, T, G, C가 있고 우라실은 RNA에 나타나."),
        ("먹이사슬에서 에너지는 일반적으로 어떻게 이동할까?", ["상위 단계로 갈수록 늘어난다", "한 방향으로 전달되며 일부가 열로 손실된다", "완전히 순환한다", "생산자에게서만 생긴다"], 1,
         "먹이 단계가 올라갈 때 에너지의 일부는 열 등으로 손실돼."),
        ("개구리의 생활사에서 일반적으로 먼저 나타나는 단계는?", ["성체", "알", "번식 가능한 성체", "겨울잠"], 1,
         "많은 개구리는 알에서 올챙이를 거쳐 성체로 자라."),
        ("광합성에 필요한 물질의 조합으로 알맞은 것은?", ["산소와 포도당", "이산화탄소와 물", "질소와 단백질", "녹말과 산소"], 1,
         "식물은 빛에너지를 이용해 이산화탄소와 물로 유기물을 만들어."),
        ("천적이 줄어들면 먹이 생물의 개체 수는 어떻게 될 수 있을까?", ["항상 0이 된다", "증가할 수 있다", "반드시 변하지 않는다", "모두 다른 종이 된다"], 1,
         "천적이 줄면 먹이 생물의 생존율이 높아져 개체 수가 증가할 수 있어."),
        ("자연선택에 대한 설명으로 알맞은 것은?", ["개체가 필요할 때 유전자를 의도적으로 바꾼다", "환경에서 번식에 유리한 유전적 특징이 다음 세대에 더 많이 전달될 수 있다", "모든 개체가 똑같이 진화한다", "진화는 한 개체의 일생에서만 일어난다"], 1,
         "자연선택은 세대에 걸쳐 집단의 유전적 특징이 달라지는 데 영향을 줘."),
        ("항생제 내성 세균이 나타나는 현상을 설명하는 데 중요한 개념은?", ["자연선택", "증발", "광합성", "삼투만"], 0,
         "항생제에 내성이 있는 세균이 살아남아 증식할 수 있어."),
        ("생물의 분류에서 종을 구분할 때 중요하게 보는 것은?", ["색깔 하나만", "여러 특징과 진화적 관계", "사는 시간만", "몸무게만"], 1,
         "생물 분류에는 형태, 유전 정보, 진화적 관계 등 여러 자료가 사용돼."),
        ("분해자의 역할은?", ["빛에너지를 직접 흡수한다", "유기물을 분해해 물질 순환에 기여한다", "모든 동물을 사냥한다", "산소를 없애기만 한다"], 1,
         "분해자는 죽은 생물과 배설물의 유기물을 분해해 물질 순환에 기여해."),
    ],
    "어려움": [
        ("제한 효소가 유전자 재조합에 활용되는 핵심 이유는?", ["DNA를 무작위로 복제하기 때문에", "특정 DNA 염기서열을 인식해 자를 수 있기 때문에", "단백질을 모두 분해하기 때문에", "세포막을 만드는 효소이기 때문에"], 1,
         "제한 효소는 특정 DNA 서열을 인식해 절단하므로 원하는 DNA 조각을 얻는 데 활용돼."),
        ("서로 다른 DNA 조각을 연결하는 데 직접적으로 사용되는 효소는?", ["DNA 연결 효소", "아밀레이스", "펩신", "락테이스"], 0,
         "DNA 연결 효소는 DNA 조각 사이의 결합을 만들어 연결해."),
        ("PCR에서 DNA를 반복적으로 복제할 때 핵심적으로 사용하는 것은?", ["DNA 중합효소", "리파아제", "셀룰레이스", "항체"], 0,
         "DNA 중합효소는 주형 DNA를 바탕으로 새로운 DNA 가닥을 합성해."),
        ("생물 집단의 유전적 다양성이 감소하면 생길 수 있는 문제는?", ["환경 변화에 대응할 가능성이 낮아질 수 있다", "모든 질병이 사라진다", "진화가 항상 빨라진다", "개체 수가 반드시 늘어난다"], 0,
         "유전적 다양성이 낮으면 새로운 환경이나 질병에 취약해질 수 있어."),
        ("세포막을 통한 물의 이동을 주로 설명하는 현상은?", ["삼투", "복제", "전사", "번역"], 0,
         "삼투는 반투과성 막을 사이에 두고 물이 이동하는 현상이야."),
        ("항상성의 의미로 가장 알맞은 것은?", ["외부 환경이 변해도 내부 상태를 일정 범위로 유지하는 것", "모든 생물이 같은 크기를 갖는 것", "에너지를 전혀 쓰지 않는 것", "유전자가 사라지는 것"], 0,
         "항상성은 체온이나 혈당처럼 몸속 상태를 일정 범위로 유지하는 능력이야."),
        ("생태계에서 특정 종이 사라졌을 때 다른 종에도 영향이 생길 수 있는 이유는?", ["생물 사이에 먹이와 서식지 관계가 있기 때문에", "모든 종이 같은 DNA를 갖기 때문에", "생물은 서로 영향을 주지 않기 때문에", "물질 순환이 없기 때문에"], 0,
         "생물은 먹이 관계와 서식지 등으로 연결되어 있어 한 종의 변화가 다른 종에도 영향을 줄 수 있어."),
        ("유전자의 발현 과정에서 DNA 정보를 RNA로 옮기는 단계는?", ["전사", "번역", "복제", "삼투"], 0,
         "전사는 DNA의 유전 정보를 RNA로 옮기는 과정이야."),
        ("번역 과정에서 아미노산을 연결해 단백질을 만드는 장소는?", ["리보솜", "리소좀", "액포", "세포벽"], 0,
         "리보솜은 mRNA 정보를 읽어 아미노산을 연결해 단백질을 합성해."),
        ("생물 농축이 일어날 가능성이 큰 물질의 특징은?", ["생물체 안에서 잘 분해되고 바로 배출된다", "잘 분해되지 않고 먹이 관계를 따라 축적될 수 있다", "물에 닿으면 즉시 사라진다", "생물에 아무 영향이 없다"], 1,
         "일부 오염 물질은 잘 분해되지 않아 먹이 관계를 따라 농도가 높아질 수 있어."),
        ("유전자 편집 기술을 평가할 때 과학적 효과 외에 고려할 사항은?", ["윤리와 안전성", "글자 수만", "색상만", "실험실 위치만"], 0,
         "유전자 편집은 생물과 사람에게 미칠 영향, 안전성, 윤리적 문제도 함께 고려해야 해."),
        ("개체군의 크기에 영향을 미치는 요인의 조합으로 알맞은 것은?", ["출생과 사망, 이입과 이출", "광합성과 소리만", "색깔과 모양만", "DNA 염기 하나만"], 0,
         "개체군 크기는 출생·사망뿐 아니라 다른 지역에서 들어오거나 나가는 개체에도 영향을 받아."),
    ],
}

# =========================================================
# 세션 상태 초기화
# 외부 저장소나 파일 저장을 사용하지 않음
# =========================================================
def initialize_state():
    defaults = {
        "discovered": {},
        "xp": 0,
        "total_found": 0,
        "quiz_correct": 0,
        "quiz_answered": 0,
        "latest_message": "",
        "latest_is_new": False,
        "page": "🌲 탐험하기",
        "quiz_difficulty": "쉬움",
        "quiz_question": None,
        "quiz_options": None,
        "quiz_answer": None,
        "quiz_explanation": None,
        "quiz_id": 0,
        "quiz_done": False,
        "quiz_feedback": None,
        "quiz_selected": None,
        "achievements_claimed": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value

initialize_state()

# =========================================================
# 게임 계산 함수
# =========================================================
def get_level(xp):
    return xp // 100 + 1

def get_level_progress(xp):
    return (xp % 100) / 100

def choose_creature():
    """아직 발견하지 못한 생물을 우선적으로 등장시킨다."""
    weights = []
    for creature in SPECIES:
        base = RARITY_INFO[creature["rarity"]]["weight"]
        if creature["name"] in st.session_state.discovered:
            weights.append(max(1, base * 0.35))
        else:
            weights.append(base * 2.8)
    return random.choices(SPECIES, weights=weights, k=1)[0]

def discover_creature():
    creature = choose_creature()
    name = creature["name"]
    is_new = name not in st.session_state.discovered

    if is_new:
        st.session_state.discovered[name] = {
            **creature,
            "count": 1,
        }
        xp_gain = RARITY_INFO[creature["rarity"]]["xp"]
        message = f"새로운 생물 발견! {name} (+{xp_gain} XP)"
    else:
        st.session_state.discovered[name]["count"] += 1
        xp_gain = 3
        message = f"{name}을(를) 다시 만났어! (+3 XP)"

    st.session_state.xp += xp_gain
    st.session_state.total_found += 1
    st.session_state.latest_message = message
    st.session_state.latest_is_new = is_new

def get_wikipedia_image(english_name):
    """위키백과 요약 API에서 생물 사진을 가져온다."""
    try:
        title = english_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        response = requests.get(
            url,
            headers={"User-Agent": "BioHunterEducationalApp/1.0"},
            timeout=4,
        )
        if response.status_code == 200:
            data = response.json()
            thumbnail = data.get("thumbnail", {}).get("source")
            if thumbnail:
                return thumbnail
    except (requests.RequestException, ValueError):
        pass
    return None

def show_creature_card(creature, compact=False):
    rarity = creature["rarity"]
    info = RARITY_INFO[rarity]
    image_url = get_wikipedia_image(creature["english"])

    st.markdown(
        f"""
        <div class="creature">
            <span class="tag">{creature['category']}</span>
            <span class="tag">{creature['habitat']}</span>
            <span class="tag" style="background:{info['color']}22;color:{info['color']}">
                {info['emoji']} {rarity}
            </span>
            <h3 style="margin-top:10px;margin-bottom:2px">{creature['name']}</h3>
            <div class="small-muted">{creature['english']}</div>
            <p>{creature['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if image_url:
        st.image(image_url, width=200 if compact else 260)
    else:
        st.info("사진을 불러오지 못했어. 생물 이름으로 검색해 봐!")

# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.markdown("# 🌿 바이오 헌터")
    st.caption("자연 속 생물을 발견하고 도감을 완성하자!")

    st.markdown("---")
    st.markdown(f"### 🧭 탐험 레벨 {get_level(st.session_state.xp)}")
    st.progress(get_level_progress(st.session_state.xp))
    st.caption(f"{st.session_state.xp % 100}/100 XP · 다음 레벨까지")

    st.markdown("---")
    st.metric("📚 발견한 종", f"{len(st.session_state.discovered)} / {len(SPECIES)}")
    st.metric("🔎 총 발견 횟수", st.session_state.total_found)

    st.markdown("---")
    page = st.radio(
        "메뉴",
        [
            "🌲 탐험하기",
            "📖 생물 도감",
            "🧬 생명과학 퀴즈",
            "🏆 업적",
            "⚙️ 설정",
        ],
        key="page",
    )

    st.markdown("---")
    st.caption("⚠️ 게임 기록은 현재 세션에서만 유지돼. 새 세션에서는 처음부터 시작해.")

# =========================================================
# 공통 헤더
# =========================================================
st.markdown("""
<div class="hero">
    <h1>🌿 바이오 헌터</h1>
    <p>숲과 강, 습지를 탐험하며 생물을 발견하고 생명과학 지식을 키워 봐!</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 탐험하기
# =========================================================
if page == "🌲 탐험하기":
    st.subheader("오늘은 어떤 생물을 만날까?")

    col1, col2, col3 = st.columns(3)
    col1.metric("🧭 탐험 레벨", get_level(st.session_state.xp))
    col2.metric("🌱 발견한 종", len(st.session_state.discovered))
    col3.metric("✨ 보유 경험치", st.session_state.xp)

    st.markdown(
        """
        <div class="panel">
        <h3>🌳 탐험 안내</h3>
        생물 발견 버튼을 눌러 새로운 생물을 찾아봐.
        처음 발견하는 생물은 희귀도에 따라 경험치를 얻고,
        이미 발견한 생물을 다시 만나면 추가 경험치를 얻을 수 있어.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔍 주변을 탐험하고 생물 발견하기", type="primary", use_container_width=True):
        discover_creature()

    if st.session_state.latest_message:
        st.success(st.session_state.latest_message)

    if st.session_state.discovered:
        latest_name = list(st.session_state.discovered.keys())[-1]
        latest_creature = st.session_state.discovered[latest_name]

        st.markdown("### 🐾 발견한 생물")
        left, right = st.columns([1, 1.2])
        with left:
            image_url = get_wikipedia_image(latest_creature["english"])
            if image_url:
                st.image(image_url, width=260)
            else:
                st.markdown("### 🌱")
                st.caption("사진을 불러오지 못했어.")
        with right:
            rarity = latest_creature["rarity"]
            info = RARITY_INFO[rarity]
            st.markdown(f"## {latest_creature['name']}")
            st.markdown(f"*{latest_creature['english']}*")
            st.markdown(
                f"<span class='tag'>{latest_creature['category']}</span>"
                f"<span class='tag'>{latest_creature['habitat']}</span>"
                f"<span class='tag' style='color:{info['color']}'>{info['emoji']} {rarity}</span>",
                unsafe_allow_html=True,
            )
            st.write(latest_creature["description"])
            st.write(f"📦 도감 보유 횟수: {latest_creature['count']}회")

    st.markdown("### 🌟 희귀도 안내")
    cols = st.columns(5)
    for col, rarity in zip(cols, RARITY_INFO):
        info = RARITY_INFO[rarity]
        with col:
            st.markdown(
                f"""
                <div class="panel" style="text-align:center;padding:12px">
                    <div style="font-size:26px">{info['emoji']}</div>
                    <b style="color:{info['color']}">{rarity}</b>
                    <div class="small-muted">최초 발견 +{info['xp']} XP</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================
# 생물 도감
# =========================================================
elif page == "📖 생물 도감":
    st.subheader("📖 나만의 생물 도감")

    total = len(st.session_state.discovered)
    st.progress(total / len(SPECIES))
    st.write(f"현재 {len(SPECIES)}종 중 **{total}종**을 발견했어.")

    filter_col1, filter_col2 = st.columns(2)
    categories = ["전체"] + sorted(set(c["category"] for c in SPECIES))
    rarities = ["전체"] + list(RARITY_INFO.keys())

    with filter_col1:
        category_filter = st.selectbox("분류", categories)
    with filter_col2:
        rarity_filter = st.selectbox("희귀도", rarities)

    discovered_only = st.toggle("발견한 생물만 보기", value=True)

    filtered = []
    for creature in SPECIES:
        found = creature["name"] in st.session_state.discovered
        if discovered_only and not found:
            continue
        if category_filter != "전체" and creature["category"] != category_filter:
            continue
        if rarity_filter != "전체" and creature["rarity"] != rarity_filter:
            continue
        filtered.append(creature)

    st.caption(f"표시 중: {len(filtered)}종")

    if not filtered:
        st.info("조건에 맞는 생물이 없어. 탐험에서 생물을 발견해 봐!")
    else:
        for start in range(0, len(filtered), 2):
            cols = st.columns(2)
            for col, creature in zip(cols, filtered[start:start + 2]):
                with col:
                    found_data = st.session_state.discovered.get(creature["name"])
                    if found_data:
                        st.markdown(f"**✅ 발견 {found_data['count']}회**")
                    else:
                        st.markdown("**🔒 미발견 생물**")
                    show_creature_card(creature, compact=True)

# =========================================================
# 생명과학 퀴즈
# =========================================================
elif page == "🧬 생명과학 퀴즈":
    st.subheader("🧬 생명과학 지식 시험")

    quiz_rewards = {"쉬움": 10, "보통": 25, "어려움": 50}
    st.write("문제를 풀고 경험치를 얻어 봐. 정답을 맞히면 선택한 난이도에 따라 보상을 받아!")

    difficulty = st.radio(
        "난이도 선택",
        ["쉬움", "보통", "어려움"],
        horizontal=True,
        key="quiz_difficulty",
    )
    st.info(f"🎁 정답 보상: {quiz_rewards[difficulty]} XP")

    if st.session_state.quiz_question is None or st.session_state.quiz_id == 0:
        question_data = random.choice(QUIZZES[difficulty])
        st.session_state.quiz_question = question_data[0]
        st.session_state.quiz_options = question_data[1]
        st.session_state.quiz_answer = question_data[2]
        st.session_state.quiz_explanation = question_data[3]
        st.session_state.quiz_done = False
        st.session_state.quiz_feedback = None
        st.session_state.quiz_selected = None
        st.session_state.quiz_current_difficulty = difficulty

    if st.session_state.get("quiz_current_difficulty") != difficulty:
        question_data = random.choice(QUIZZES[difficulty])
        st.session_state.quiz_question = question_data[0]
        st.session_state.quiz_options = question_data[1]
        st.session_state.quiz_answer = question_data[2]
        st.session_state.quiz_explanation = question_data[3]
        st.session_state.quiz_done = False
        st.session_state.quiz_feedback = None
        st.session_state.quiz_selected = None
        st.session_state.quiz_current_difficulty = difficulty
        st.session_state.quiz_id += 1

    st.markdown(
        f"""
        <div class="panel">
            <div class="small-muted">{difficulty} 난이도 · 문제</div>
            <h3>{st.session_state.quiz_question}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    answer_key = f"quiz_answer_{st.session_state.quiz_id}_{difficulty}"
    selected = st.radio(
        "정답을 선택해 줘.",
        st.session_state.quiz_options,
        key=answer_key,
        index=None,
        disabled=st.session_state.quiz_done,
    )

    if not st.session_state.quiz_done:
        if st.button("정답 확인하기", type="primary", use_container_width=True):
            if selected is None:
                st.warning("답을 하나 선택해 줘!")
            else:
                selected_index = st.session_state.quiz_options.index(selected)
                st.session_state.quiz_done = True
                st.session_state.quiz_selected = selected_index
                st.session_state.quiz_answered += 1

                if selected_index == st.session_state.quiz_answer:
                    reward = quiz_rewards[difficulty]
                    st.session_state.xp += reward
                    st.session_state.quiz_correct += 1
                    st.session_state.quiz_feedback = ("correct", reward)
                else:
                    st.session_state.quiz_feedback = ("wrong", 0)
                st.rerun()

    if st.session_state.quiz_done and st.session_state.quiz_feedback:
        status, reward = st.session_state.quiz_feedback
        if status == "correct":
            st.success(f"🎉 정답이야! 경험치 +{reward} XP")
        else:
            correct_answer = st.session_state.quiz_options[st.session_state.quiz_answer]
            st.error(f"아쉽지만 오답이야. 정답은 **{correct_answer}** 이야.")

        st.info(st.session_state.quiz_explanation)

        if st.button("다음 문제 풀기 ➜", use_container_width=True):
            question_data = random.choice(QUIZZES[difficulty])
            st.session_state.quiz_question = question_data[0]
            st.session_state.quiz_options = question_data[1]
            st.session_state.quiz_answer = question_data[2]
            st.session_state.quiz_explanation = question_data[3]
            st.session_state.quiz_done = False
            st.session_state.quiz_feedback = None
            st.session_state.quiz_selected = None
            st.session_state.quiz_id += 1
            st.rerun()

    st.markdown("---")
    q1, q2, q3 = st.columns(3)
    q1.metric("📝 푼 문제", st.session_state.quiz_answered)
    q2.metric("✅ 맞힌 문제", st.session_state.quiz_correct)
    accuracy = (
        round(st.session_state.quiz_correct / st.session_state.quiz_answered * 100)
        if st.session_state.quiz_answered else 0
    )
    q3.metric("🎯 정답률", f"{accuracy}%")

# =========================================================
# 업적
# =========================================================
elif page == "🏆 업적":
    st.subheader("🏆 탐험 업적")

    discovered_count = len(st.session_state.discovered)
    rarity_count = {
        rarity: sum(
            1 for c in st.session_state.discovered.values()
            if c["rarity"] == rarity
        )
        for rarity in RARITY_INFO
    }

    achievements = [
        ("🌱 첫 발견", "생물을 1종 발견하기", discovered_count >= 1),
        ("🍀 초보 탐험가", "생물을 5종 발견하기", discovered_count >= 5),
        ("🌳 숲의 친구", "생물을 15종 발견하기", discovered_count >= 15),
        ("🦉 자연 관찰가", "생물을 30종 발견하기", discovered_count >= 30),
        ("📚 도감 수집가", "생물을 50종 발견하기", discovered_count >= 50),
        ("🌏 생태계 전문가", "생물을 80종 발견하기", discovered_count >= 80),
        ("👑 전설의 발견자", "전설 생물을 발견하기", rarity_count["전설"] >= 1),
        ("💎 희귀 수집가", "희귀 생물 5종 발견하기", rarity_count["희귀"] >= 5),
        ("🧬 생명과학 도전자", "퀴즈 5문제 풀기", st.session_state.quiz_answered >= 5),
        ("🎓 생명과학 우등생", "퀴즈 10문제 맞히기", st.session_state.quiz_correct >= 10),
        ("✨ 레벨 5 달성", "탐험 레벨 5에 도달하기", get_level(st.session_state.xp) >= 5),
    ]

    unlocked = sum(1 for _, _, done in achievements if done)
    st.progress(unlocked / len(achievements))
    st.write(f"달성한 업적: **{unlocked}/{len(achievements)}**")

    for title, description, done in achievements:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"### {title if done else '🔒 ' + title}")
                st.caption(description)
            with right:
                st.markdown("### ✅" if done else "🔒")

    st.markdown("### 희귀도별 발견 현황")
    for rarity, count in rarity_count.items():
        info = RARITY_INFO[rarity]
        st.write(f"{info['emoji']} **{rarity}** — {count}종")

# =========================================================
# 설정
# =========================================================
elif page == "⚙️ 설정":
    st.subheader("⚙️ 게임 설정")

    st.markdown(
        """
        <div class="panel">
            <h3>🌿 바이오 헌터 안내</h3>
            <p>바이오 헌터는 생물 관찰과 생명과학 학습을 위한 간단한 탐험 게임이야.</p>
            <p>생물 사진은 위키백과에서 불러올 수 있으며, 인터넷 연결이 필요해.</p>
            <p>생물 이름에 따라 사진이 없거나 다른 이미지가 표시될 수도 있어.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 현재 플레이 현황")
    st.write(f"- 탐험 레벨: {get_level(st.session_state.xp)}")
    st.write(f"- 경험치: {st.session_state.xp} XP")
    st.write(f"- 발견한 생물: {len(st.session_state.discovered)}종")
    st.write(f"- 총 발견 횟수: {st.session_state.total_found}회")
    st.write(f"- 퀴즈 정답: {st.session_state.quiz_correct}개")

    st.warning(
        "이 버전은 기록을 파일이나 데이터베이스에 저장하지 않아. "
        "현재 세션이 끝나면 도감, 경험치, 업적 진행 상황이 초기화돼."
    )

    st.markdown("### 🧹 현재 기록 초기화")
    st.caption("현재 세션의 진행 상황만 초기화할 수 있어. 되돌릴 수 없어.")

    confirm_reset = st.checkbox("현재 플레이 기록을 초기화하겠습니다.")

    if st.button("🔄 처음부터 다시 시작", disabled=not confirm_reset):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_state()
        st.rerun()

# =========================================================
# 하단 안내
# =========================================================
st.markdown("---")
st.caption(
    "🌿 바이오 헌터 · 생물에 대한 설명은 학습용 요약이야. "
    "실제 야생 생물을 관찰할 때는 서식지를 훼손하거나 동물을 만지지 말자."
)
