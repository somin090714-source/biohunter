import random
import requests
import streamlit as st
from urllib.parse import quote

st.set_page_config(page_title="바이오 헌터", page_icon="🌿", layout="wide")

st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#f2f8ec,#fffdf6);}
h1,h2,h3 {color:#28583a;}
div.stButton>button {border-radius:12px;min-height:42px;font-weight:600;}
div.stButton>button[kind="primary"] {background:#39764c;border-color:#39764c;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 1. 지형과 희귀도
# =========================================================

TERRAINS = {
    "숲": {"emoji":"🌲","habitats":["숲"],"description":"나무와 숲속 생물"},
    "호수·연못": {"emoji":"🏞️","habitats":["호수","연못"],"description":"물속과 물가의 생물"},
    "바다": {"emoji":"🌊","habitats":["바다"],"description":"바다와 해안의 생물"},
    "산": {"emoji":"⛰️","habitats":["산"],"description":"산과 바위 주변의 생물"},
    "초원": {"emoji":"🌾","habitats":["초원"],"description":"풀밭과 들판의 생물"},
    "습지": {"emoji":"🐸","habitats":["습지"],"description":"늪과 습지의 생물"},
}

RARITY_INFO = {
    "일반":{"weight":58,"xp":10,"emoji":"🍃"},
    "고급":{"weight":25,"xp":20,"emoji":"🌿"},
    "희귀":{"weight":12,"xp":40,"emoji":"💎"},
    "초희귀":{"weight":4,"xp":80,"emoji":"✨"},
    "전설":{"weight":1,"xp":150,"emoji":"👑"},
}
RARITY_ORDER = list(RARITY_INFO)

# =========================================================
# 2. 생물 도감 데이터
# 형식: 이름|분류|서식지|희귀도|설명|이모지
# 생물 이름은 도감에서 중복되지 않도록 관리한다.
# =========================================================

RAW_SPECIES = r"""
참개구리|양서류|연못,습지|일반|논과 연못 주변에서 볼 수 있는 개구리|🐸
청개구리|양서류|숲,습지|고급|나뭇잎과 풀 위에서 생활하는 작은 개구리|🐸
도롱뇽|양서류|숲,습지|고급|축축한 숲 바닥과 물가에서 발견되는 양서류|🦎
맹꽁이|양서류|초원,습지|희귀|비가 오는 시기에 땅속에서 나와 활동하는 개구리|🐸
금개구리|양서류|연못,습지|희귀|습지와 논 주변에서 살아가는 우리나라의 개구리|🐸
두꺼비|양서류|숲,초원|일반|피부가 울퉁불퉁한 양서류|🐸
산개구리|양서류|산,숲|고급|산지 계곡과 숲 주변에서 볼 수 있는 개구리|🐸
수달|포유류|호수,연못,습지|희귀|물고기를 잡아먹으며 물가에서 생활하는 포유류|🦦
고라니|포유류|숲,습지|일반|숲과 풀밭에서 볼 수 있는 사슴과 동물|🦌
너구리|포유류|숲,산|일반|숲과 산 주변에서 다양한 먹이를 먹는 포유류|🦝
오소리|포유류|숲,산|고급|땅을 파서 굴을 만들고 생활하는 포유류|🦡
멧돼지|포유류|숲,산|고급|잡식성이며 숲속을 돌아다니는 동물|🐗
다람쥐|포유류|숲,산|일반|도토리와 씨앗 등을 모아 먹는 작은 포유류|🐿️
청설모|포유류|숲|일반|나무를 잘 타며 열매와 씨앗을 먹는 동물|🐿️
산양|포유류|산|초희귀|가파른 바위산에서 생활하는 초식동물|🐐
삵|포유류|숲,습지|희귀|우리나라에 서식하는 야생 고양잇과 동물|🐈
하늘다람쥐|포유류|숲|희귀|몸 옆의 막을 이용해 나무 사이를 활공하는 동물|🐿️
담비|포유류|숲,산|희귀|숲에서 작은 동물과 열매를 먹는 포유류|🦦
고슴도치|포유류|숲,초원|고급|등에 난 가시로 몸을 보호하는 작은 포유류|🦔
박쥐|포유류|숲,산|고급|날개로 날며 많은 종류가 밤에 활동하는 포유류|🦇
두더지|포유류|숲,초원|일반|땅속을 파며 생활하는 포유류|🐾
족제비|포유류|숲,습지|고급|몸이 길고 작은 동물을 사냥하는 포유류|🦦
노루|포유류|숲,산|고급|숲과 산에서 식물을 먹는 사슴과 동물|🦌
사향노루|포유류|산|초희귀|산림에 사는 작은 사슴과 포유류|🦌
반달가슴곰|포유류|산,숲|전설|가슴의 초승달 모양 무늬가 특징인 곰|🐻
늑대|포유류|산,숲|전설|무리를 이루어 생활할 수 있는 개과 동물|🐺
여우|포유류|산,초원|희귀|뾰족한 주둥이와 풍성한 꼬리가 특징인 포유류|🦊
토끼|포유류|초원,숲|일반|식물을 주로 먹는 초식성 포유류|🐇
멧토끼|포유류|산,초원|고급|산과 들에서 생활하는 야생 토끼|🐇
고래|포유류|바다|전설|물속에서 생활하는 대형 포유류|🐋
혹등고래|포유류|바다|전설|긴 가슴지느러미와 도약 행동으로 알려진 고래|🐋
남방큰돌고래|포유류|바다|희귀|제주도 주변 바다에서 관찰되는 돌고래|🐬
점박이물범|포유류|바다|희귀|몸에 점무늬가 있는 바다 포유류|🦭
바다사자|포유류|바다|희귀|지느러미를 이용해 헤엄치는 해양 포유류|🦭
범고래|포유류|바다|전설|무리 생활과 협동 사냥으로 알려진 해양 포유류|🐋
참새|조류|숲,초원|일반|사람이 사는 곳 주변에서도 흔히 볼 수 있는 작은 새|🐦
까치|조류|숲,초원|일반|검은색과 흰색 깃털이 특징인 새|🐦
까마귀|조류|숲,산|일반|뛰어난 학습 능력을 보이는 새|🐦‍⬛
박새|조류|숲|일반|나무 사이를 오가며 곤충을 잡아먹는 작은 새|🐦
물총새|조류|호수,연못|고급|물속으로 뛰어들어 물고기를 잡는 새|🐦
왜가리|조류|호수,연못,습지|고급|긴 다리로 물가를 걸으며 물고기를 사냥하는 새|🪶
백로|조류|호수,연못,습지|고급|흰 깃털과 긴 다리가 특징인 물새|🪶
원앙|조류|호수,연못|희귀|수컷의 화려한 깃털이 특징인 오리류|🦆
수리부엉이|조류|숲,산|희귀|큰 눈과 귀깃이 특징인 야행성 맹금류|🦉
황조롱이|조류|초원,산|고급|공중에서 정지 비행을 하며 먹이를 찾는 맹금류|🦅
큰고니|조류|호수,연못,습지|희귀|겨울철 물가에서 관찰할 수 있는 큰 물새|🦢
노랑부리저어새|조류|습지|희귀|주걱처럼 생긴 부리로 물속 먹이를 찾는 새|🪶
후투티|조류|초원,숲|고급|머리의 독특한 깃털 장식이 눈에 띄는 새|🐦
딱따구리|조류|숲|고급|나무를 두드려 곤충을 찾는 새|🐦
제비|조류|초원,습지|일반|날면서 곤충을 잡아먹는 새|🐦
꿩|조류|초원,숲|일반|땅 위에서 먹이를 찾는 새|🐦
독수리|조류|산|희귀|큰 날개를 이용해 활공하는 맹금류|🦅
참매|조류|숲,산|희귀|빠르게 날아 먹이를 사냥하는 맹금류|🦅
흰꼬리수리|조류|바다,습지|전설|큰 날개와 흰 꼬리가 특징인 맹금류|🦅
두루미|조류|습지,초원|전설|긴 다리와 목을 가진 큰 새|🪶
재두루미|조류|습지|희귀|습지와 농경지에서 관찰되는 두루미류|🪶
기러기|조류|습지,호수|고급|무리를 이루어 이동하는 물새|🪿
청둥오리|조류|호수,연못|일반|호수와 연못에서 흔히 볼 수 있는 오리|🦆
물닭|조류|호수,습지|일반|물가에서 먹이를 찾는 물새|🐦
논병아리|조류|호수,연못|고급|물속으로 잠수해 먹이를 찾는 새|🐦
갈매기|조류|바다|일반|해안에서 자주 관찰되는 바닷새|🐦
바다제비|조류|바다|희귀|넓은 바다 위를 날아다니는 바닷새|🐦
펭귄|조류|바다|희귀|날개가 지느러미처럼 발달해 헤엄치는 새|🐧
타조|조류|초원|희귀|날지 못하지만 달리기에 적합한 큰 새|🐦
공작|조류|숲|희귀|수컷의 화려한 꼬리깃으로 알려진 새|🦚
잉어|어류|호수,연못|일반|민물에서 생활하며 다양한 먹이를 먹는 물고기|🐟
붕어|어류|호수,연못|일반|연못과 호수에서 흔히 볼 수 있는 민물고기|🐟
피라미|어류|호수,연못|일반|하천에서 무리 지어 생활하는 작은 물고기|🐟
미꾸라지|어류|호수,연못,습지|일반|진흙이 있는 얕은 물에서 생활하는 물고기|🐟
메기|어류|호수,연못|고급|입 주변의 수염으로 먹이를 찾는 민물고기|🐟
쏘가리|어류|호수,연못|고급|다른 물고기를 잡아먹는 민물고기|🐟
은어|어류|호수,연못|고급|맑은 물에서 생활하며 조류를 먹는 물고기|🐟
연어|어류|바다|고급|성장 후 바다에서 생활하고 산란기에 강으로 돌아오는 물고기|🐟
장어|어류|호수,연못,바다|희귀|성장 단계에 따라 서식 환경이 달라지는 물고기|🐟
철갑상어|어류|바다|희귀|단단한 골판이 몸을 덮고 있는 물고기 무리|🐟
꺽지|어류|호수,연못|고급|우리나라의 맑은 하천에서 볼 수 있는 민물고기|🐟
빙어|어류|호수,연못|고급|차가운 호수에서 생활하는 작은 물고기|🐟
가물치|어류|호수,연못,습지|고급|산소가 부족한 환경에서도 잘 견디는 물고기|🐟
복어|어류|바다|고급|위협을 받으면 몸을 부풀리는 물고기|🐡
흰동가리|어류|바다|고급|말미잘과 함께 생활하는 주황색 물고기|🐠
참치|어류|바다|고급|빠르게 헤엄치는 대형 바닷물고기|🐟
고등어|어류|바다|일반|무리를 이루어 이동하는 바닷물고기|🐟
멸치|어류|바다|일반|작은 몸으로 무리를 이루는 바닷물고기|🐟
정어리|어류|바다|일반|큰 무리를 이루어 생활하는 작은 물고기|🐟
갈치|어류|바다|일반|몸이 길고 은빛을 띠는 바닷물고기|🐟
광어|어류|바다|일반|바닥 가까이에서 생활하는 납작한 물고기|🐟
가자미|어류|바다|일반|몸의 양쪽 눈이 한쪽으로 모여 있는 물고기|🐟
명태|어류|바다|일반|차가운 바다에서 생활하는 물고기|🐟
대구|어류|바다|고급|차가운 바다에서 먹이를 찾는 물고기|🐟
아귀|어류|바다|고급|머리 앞쪽의 돌기로 먹이를 유인하는 물고기|🐟
해마|어류|바다|희귀|몸이 말과 비슷하며 수컷이 알을 품는 물고기|🐴
쏠배감펭|어류|바다|희귀|화려한 지느러미와 독가시가 특징인 물고기|🐠
만타가오리|어류|바다|전설|넓은 가슴지느러미로 헤엄치는 대형 어류|🐟
백상아리|어류|바다|전설|큰 몸집과 날카로운 이빨을 가진 상어|🦈
고래상어|어류|바다|전설|현존하는 가장 큰 어류로 알려진 상어|🦈
흰상어|어류|바다|전설|큰 몸집을 가진 상어류|🦈
해파리|무척추동물|바다|일반|촉수와 몸의 움직임으로 물속을 떠다니는 동물|🪼
문어|무척추동물|바다|고급|여덟 개의 팔과 뛰어난 위장 능력이 특징인 동물|🐙
오징어|무척추동물|바다|일반|물속에서 빠르게 이동하는 두족류|🦑
대왕오징어|무척추동물|바다|전설|매우 큰 몸집으로 알려진 심해 오징어류|🦑
불가사리|무척추동물|바다|일반|팔이 여러 개이며 바다 바닥에서 생활하는 동물|⭐
성게|무척추동물|바다|일반|가시로 몸을 보호하는 해양 무척추동물|🦔
산호|무척추동물|바다|고급|작은 동물들이 모여 군체를 이루는 해양 생물|🪸
해면동물|무척추동물|바다|일반|물속에서 물을 걸러 먹이를 얻는 동물|🪸
바다거북|파충류|바다|희귀|바다에서 생활하며 알을 낳을 때 육지로 올라오는 파충류|🐢
푸른바다거북|파충류|바다|희귀|해초와 해조류 등을 먹는 바다거북|🐢
남생이|파충류|연못,습지|희귀|민물에서 생활하는 우리나라의 토종 거북|🐢
자라|파충류|호수,연못|고급|부드러운 가죽 같은 등딱지가 특징인 거북|🐢
살모사|파충류|숲,산|희귀|독을 가진 뱀으로 야생에서 주의해야 하는 동물|🐍
구렁이|파충류|숲,산|고급|몸이 길고 작은 동물을 먹는 뱀|🐍
도마뱀|파충류|숲,산|일반|비늘로 덮인 피부를 가진 파충류|🦎
바다이구아나|파충류|바다|희귀|바다에서 먹이를 찾는 이구아나류|🦎
카멜레온|파충류|숲|희귀|주변 환경에 따라 피부색이 달라질 수 있는 파충류|🦎
악어|파충류|습지|희귀|물가에서 사냥하는 대형 파충류|🐊
코모도왕도마뱀|파충류|초원|전설|큰 몸집을 가진 왕도마뱀류|🦎
꿀벌|곤충|숲,초원|일반|꽃가루받이를 돕고 꿀을 만드는 사회성 곤충|🐝
호랑나비|곤충|숲,초원|고급|노란색과 검은색 무늬가 특징인 나비|🦋
장수풍뎅이|곤충|숲|고급|수컷의 큰 뿔이 특징인 딱정벌레|🪲
사슴벌레|곤충|숲|고급|큰 턱으로 알려진 딱정벌레|🪲
무당벌레|곤충|숲,초원|일반|진딧물 등을 먹는 딱정벌레|🐞
잠자리|곤충|호수,연못,습지|일반|날개가 두 쌍이며 날아다니는 곤충|🪰
반딧불이|곤충|숲,습지|희귀|빛을 내는 발광 기관이 있는 곤충|✨
사마귀|곤충|초원,숲|고급|앞다리로 먹이를 붙잡는 포식성 곤충|🦗
장수잠자리|곤충|연못,습지|고급|큰 몸과 빠른 비행이 특징인 잠자리|🪰
물방개|곤충|연못,습지|일반|뒷다리를 이용해 물속을 헤엄치는 수서곤충|🪲
물자라|곤충|연못,습지|고급|물속에서 작은 동물을 사냥하는 곤충|🪲
왕잠자리|곤충|연못,습지|고급|연못 주변에서 빠르게 날아다니는 잠자리|🪰
길앞잡이|곤충|초원,산|고급|빠르게 달리며 작은 곤충을 사냥하는 딱정벌레|🪲
제비나비|곤충|숲,초원|고급|검은 날개와 꼬리 모양 돌기가 특징인 나비|🦋
큰줄흰나비|곤충|초원|일반|흰 날개에 검은 무늬가 있는 나비|🦋
개미|곤충|숲,초원|일반|무리를 이루어 협력하는 사회성 곤충|🐜
흰개미|곤충|숲|고급|나무 속에서 생활하며 군체를 이루는 곤충|🐜
모기|곤충|습지,연못|일반|물에서 유충 시기를 보내는 곤충|🦟
파리|곤충|숲,초원|일반|한 쌍의 날개를 가진 곤충|🪰
나방|곤충|숲|일반|많은 종류가 밤에 활동하는 비늘날개 곤충|🦋
누에나방|곤충|숲|고급|누에의 성충으로 실크 생산과 관련된 곤충|🦋
매미|곤충|숲|일반|수컷이 소리를 내어 짝을 찾는 곤충|🪲
귀뚜라미|곤충|초원|일반|뒷다리가 발달한 곤충|🦗
여치|곤충|초원|일반|긴 더듬이를 가진 메뚜기류 곤충|🦗
메뚜기|곤충|초원|일반|뒷다리가 발달해 도약하는 곤충|🦗
방아깨비|곤충|초원|일반|풀밭에서 발견되는 메뚜기류 곤충|🦗
풀무치|곤충|초원|고급|몸집이 큰 메뚜기류 곤충|🦗
노린재|곤충|숲,초원|일반|특유의 체취를 내는 종류가 있는 곤충|🪲
매미충|곤충|숲,초원|일반|식물의 즙을 먹는 작은 곤충|🪲
진딧물|곤충|숲,초원|일반|식물의 즙을 빨아먹는 작은 곤충|🐜
하늘소|곤충|숲|고급|긴 더듬이가 특징인 딱정벌레류|🪲
반날개|곤충|숲|고급|짧은 딱지날개가 특징인 딱정벌레류|🪲
물장군|곤충|연못,습지|희귀|물속에서 작은 동물을 사냥하는 큰 수서곤충|🪲
소금쟁이|곤충|연못,습지|일반|물 표면 위를 걸어 다니는 곤충|🪲
장구애비|곤충|연못,습지|고급|긴 호흡관을 가진 수서곤충|🪲
물매암이|곤충|연못,습지|일반|물 표면을 빙글빙글 돌며 움직이는 곤충|🪲
왕사마귀|곤충|초원,숲|고급|큰 몸집과 사냥에 적합한 앞다리가 특징인 곤충|🦗
꽃등에|곤충|숲,초원|일반|벌과 비슷하게 보이는 파리류 곤충|🐝
뒤영벌|곤충|숲,초원|고급|꽃가루받이에 중요한 역할을 하는 곤충|🐝
호박벌|곤충|숲,초원|고급|털이 많은 몸으로 알려진 벌류|🐝
왕나비|곤충|초원|희귀|큰 날개를 가진 나비류|🦋
제주왕나비|곤충|초원|희귀|섬과 해안 환경에서 관찰되는 나비류|🦋
푸른부전나비|곤충|초원|고급|푸른빛 날개가 특징인 작은 나비|🦋
배추흰나비|곤충|초원|일반|배추 등 십자화과 식물과 관련된 나비|🦋
네발나비|곤충|숲,초원|일반|날개 무늬가 다양한 나비류|🦋
왕오색나비|곤충|숲|희귀|날개에 여러 색의 광택이 나타나는 나비|🦋
민들레|식물|초원|일반|씨앗이 바람을 타고 퍼지는 꽃식물|🌼
소나무|식물|숲,산|일반|바늘 모양 잎을 가진 상록수|🌲
은행나무|식물|숲,초원|일반|부채 모양 잎을 가진 나무|🌳
벚나무|식물|숲,산|일반|봄에 꽃을 피우는 나무|🌸
해바라기|식물|초원|일반|큰 꽃과 씨앗으로 잘 알려진 식물|🌻
연꽃|식물|연못,습지|고급|물 위로 잎과 꽃을 높이 올리는 수생식물|🪷
끈끈이주걱|식물|습지|희귀|끈끈한 잎으로 작은 곤충을 붙잡는 식충식물|🌱
파리지옥|식물|습지|희귀|잎을 빠르게 닫아 작은 먹이를 붙잡는 식물|🌿
주목|식물|산,숲|고급|늘푸른 잎을 가진 나무|🌲
으름덩굴|식물|숲|일반|덩굴로 자라며 열매가 열리는 식물|🌿
산철쭉|식물|산|일반|봄에 분홍색 계열의 꽃을 피우는 관목|🌺
억새|식물|초원,산|일반|가을에 은빛 꽃차례가 돋보이는 풀|🌾
갈대|식물|습지,연못|일반|물가와 습지에서 무리 지어 자라는 키 큰 풀|🌾
# =========================================================
# 3. 생물 데이터 정리 및 정보 링크
# =========================================================

def parse_species(raw_data):
    species = []
    for line in raw_data.strip().splitlines():
        parts = line.strip().split("|")
        if len(parts) != 6:
            continue

        name, category, habitat_text, rarity, description, emoji = parts

        species.append({
            "name": name,
            "category": category,
            "habitats": habitat_text.split(","),
            "rarity": rarity,
            "description": description,
            "emoji": emoji,
        })

    return species


SPECIES = parse_species(RAW_SPECIES)


def get_info_url(creature_name):
    """생물 이름으로 한국어 위키백과 검색 페이지 주소를 만든다."""
    return (
        "https://ko.wikipedia.org/wiki/Special:Search?search="
        + quote(creature_name)
    )


def get_creature_image(creature_name):
    """위키백과에서 생물 이미지를 찾아 표시한다."""
    try:
        url = "https://ko.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": creature_name,
            "gsrnamespace": 6,
            "gsrlimit": 1,
            "prop": "imageinfo",
            "iiprop": "url",
        }
        response = requests.get(
            url,
            params=params,
            timeout=5,
            headers={"User-Agent": "BioHunter/1.0"}
        )
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            image_info = page.get("imageinfo", [])
            if image_info:
                image_url = image_info[0].get("url", "")
                if image_url.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".webp", ".gif")
                ):
                    return image_url

    except (requests.RequestException, ValueError, KeyError):
        pass

    return None


# =========================================================
# 4. 퀴즈 데이터
# =========================================================

RAW_QUIZZES = r"""
참개구리|양서류|연못,습지|논과 연못 주변에서 볼 수 있는 개구리
청개구리|양서류|숲,습지|나뭇잎과 풀 위에서 생활하는 작은 개구리
수달|포유류|호수,연못,습지|물고기를 잡아먹으며 물가에서 생활하는 포유류
고라니|포유류|숲,습지|숲과 풀밭에서 볼 수 있는 사슴과 동물
너구리|포유류|숲,산|숲과 산 주변에서 다양한 먹이를 먹는 포유류
다람쥐|포유류|숲,산|도토리와 씨앗 등을 모아 먹는 작은 포유류
반달가슴곰|포유류|산,숲|가슴의 초승달 모양 무늬가 특징인 곰
여우|포유류|산,초원|뾰족한 주둥이와 풍성한 꼬리가 특징인 포유류
참새|조류|숲,초원|사람이 사는 곳 주변에서도 흔히 볼 수 있는 작은 새
까치|조류|숲,초원|검은색과 흰색 깃털이 특징인 새
물총새|조류|호수,연못|물속으로 뛰어들어 물고기를 잡는 새
수리부엉이|조류|숲,산|큰 눈과 귀깃이 특징인 야행성 맹금류
청둥오리|조류|호수,연못|호수와 연못에서 흔히 볼 수 있는 오리
펭귄|조류|바다|날개가 지느러미처럼 발달해 헤엄치는 새
잉어|어류|호수,연못|민물에서 생활하며 다양한 먹이를 먹는 물고기
메기|어류|호수,연못|입 주변의 수염으로 먹이를 찾는 민물고기
연어|어류|바다|성장 후 바다에서 생활하고 산란기에 강으로 돌아오는 물고기
복어|어류|바다|위협을 받으면 몸을 부풀리는 물고기
해마|어류|바다|몸이 말과 비슷하며 수컷이 알을 품는 물고기
고래상어|어류|바다|현존하는 가장 큰 어류로 알려진 상어
문어|무척추동물|바다|여덟 개의 팔과 뛰어난 위장 능력이 특징인 동물
해파리|무척추동물|바다|촉수와 몸의 움직임으로 물속을 떠다니는 동물
바다거북|파충류|바다|바다에서 생활하며 알을 낳을 때 육지로 올라오는 파충류
카멜레온|파충류|숲|주변 환경에 따라 피부색이 달라질 수 있는 파충류
꿀벌|곤충|숲,초원|꽃가루받이를 돕고 꿀을 만드는 사회성 곤충
호랑나비|곤충|숲,초원|노란색과 검은색 무늬가 특징인 나비
장수풍뎅이|곤충|숲|수컷의 큰 뿔이 특징인 딱정벌레
무당벌레|곤충|숲,초원|진딧물 등을 먹는 딱정벌레
반딧불이|곤충|숲,습지|빛을 내는 발광 기관이 있는 곤충
사마귀|곤충|초원,숲|앞다리로 먹이를 붙잡는 포식성 곤충
민들레|식물|초원|씨앗이 바람을 타고 퍼지는 꽃식물
소나무|식물|숲,산|바늘 모양 잎을 가진 상록수
은행나무|식물|숲,초원|부채 모양 잎을 가진 나무
해바라기|식물|초원|큰 꽃과 씨앗으로 잘 알려진 식물
연꽃|식물|연못,습지|물 위로 잎과 꽃을 높이 올리는 수생식물
파리지옥|식물|습지|잎을 빠르게 닫아 작은 먹이를 붙잡는 식물
"""

def parse_quizzes(raw_data):
    quizzes = []

    for line in raw_data.strip().splitlines():
        parts = line.strip().split("|")

        if len(parts) != 4:
            continue

        name, category, habitat_text, description = parts

        quizzes.append({
            "name": name,
            "category": category,
            "habitats": habitat_text.split(","),
            "description": description,
        })

    return quizzes


QUIZZES = parse_quizzes(RAW_QUIZZES)


# =========================================================
# 5. 게임 상태 초기화
# =========================================================

def initialize_game():
    defaults = {
        "xp": 0,
        "level": 1,
        "discovered": [],
        "attempted": [],
        "quiz_correct": 0,
        "quiz_total": 0,
        "exploration_count": 0,
        "current_creature": None,
        "last_result": None,
        "last_terrain": "숲",
        "page": "🏠 홈",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


initialize_game()


def add_xp(amount):
    st.session_state.xp += amount
    new_level = st.session_state.xp // 100 + 1

    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.balloons()
        st.success(f"🎉 레벨 업! 현재 레벨은 {new_level}입니다!")


def get_level_title(level):
    if level >= 10:
        return "🏆 생태계 마스터"
    if level >= 7:
        return "🌟 생물 전문가"
    if level >= 4:
        return "🔬 생물 연구원"
    if level >= 2:
        return "🌱 견습 탐험가"
    return "🧭 초보 탐험가"


def discover_creature(creature):
    name = creature["name"]

    if name in st.session_state.discovered:
        return "duplicate"

    st.session_state.discovered.append(name)
    add_xp(RARITY_INFO[creature["rarity"]]["xp"])
    return "new"


# =========================================================
# 6. 공통 화면
# =========================================================

st.title("🌿 바이오 헌터")
st.caption("여러 지형을 탐험하며 다양한 생물을 발견하고 도감을 완성해 보세요!")

with st.sidebar:
    st.header("🧭 탐험가 정보")
    st.metric("레벨", st.session_state.level)
    st.write(get_level_title(st.session_state.level))
    st.progress((st.session_state.xp % 100) / 100)
    st.caption(f"경험치: {st.session_state.xp % 100}/100")
    st.metric("발견한 생물", f"{len(st.session_state.discovered)} / {len(SPECIES)}")
    st.metric("퀴즈 정답", st.session_state.quiz_correct)

    st.divider()
    page = st.radio(
        "메뉴",
        ["🏠 홈", "🌎 탐험하기", "📚 생물 도감", "🧠 생물 퀴즈", "🏆 업적"],
        key="navigation",
    )


# =========================================================
# 7. 홈 화면
# =========================================================

if page == "🏠 홈":
    st.header("환영합니다, 탐험가님! 🌱")
    st.write(
        "바이오 헌터에서는 숲, 바다, 산, 초원 등 다양한 환경을 탐험하며 "
        "그곳에 사는 생물들을 발견할 수 있어요."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("현재 레벨", st.session_state.level)
    col2.metric("발견한 생물", len(st.session_state.discovered))
    col3.metric("탐험 횟수", st.session_state.exploration_count)

    st.subheader("🎯 이렇게 플레이해 보세요")
    st.markdown("""
    1. **탐험하기** 메뉴에서 지형을 선택하세요.
    2. 탐험을 진행해 새로운 생물을 발견하세요.
    3. 발견한 생물은 **생물 도감**에서 확인할 수 있어요.
    4. **생물 퀴즈**를 풀어 생물에 대한 지식을 확인하세요.
    5. 경험치를 모아 레벨을 올리고 업적을 달성해 보세요.
    """)

    st.info("💡 팁: 모든 생물을 발견하고 도감을 완성해 보세요!")


# =========================================================
# 8. 탐험 화면
# =========================================================

elif page == "🌎 탐험하기":
    st.header("🌎 생물 탐험")
    st.write("탐험할 지형을 선택하고 그곳에 사는 생물을 찾아보세요.")

    terrain = st.selectbox(
        "탐험 지역",
        list(TERRAINS.keys()),
        key="selected_terrain",
    )

    terrain_info = TERRAINS[terrain]
    st.subheader(f"{terrain_info['emoji']} {terrain}")
    st.write(terrain_info["description"])

    if st.button("🔎 탐험 시작하기", type="primary", use_container_width=True):
        st.session_state.exploration_count += 1
        st.session_state.last_terrain = terrain

        possible = [
            creature for creature in SPECIES
            if any(h in terrain_info["habitats"] for h in creature["habitats"])
        ]

        if not possible:
            st.warning("이 지형에서 발견할 수 있는 생물이 없습니다.")
            st.session_state.current_creature = None
        else:
            rarity_weights = [
                RARITY_INFO[creature["rarity"]]["weight"]
                for creature in possible
            ]
            creature = random.choices(
                possible,
                weights=rarity_weights,
                k=1,
            )[0]

            st.session_state.current_creature = creature
            st.session_state.last_result = discover_creature(creature)

    creature = st.session_state.current_creature

    if creature and st.session_state.last_terrain == terrain:
        st.divider()
        result = st.session_state.last_result

        if result == "new":
            st.success("🎉 새로운 생물을 발견했어요!")
        elif result == "duplicate":
            st.info("👀 이미 발견한 생물이에요. 다른 생물도 찾아보세요!")

        rarity = creature["rarity"]
        st.subheader(
            f"{creature['emoji']} {creature['name']} "
            f"{RARITY_INFO[rarity]['emoji']} {rarity}"
        )
        st.write(f"**분류:** {creature['category']}")
        st.write(f"**서식지:** {', '.join(creature['habitats'])}")
        st.write(f"**특징:** {creature['description']}")

        # 새로 발견했거나 이미 발견한 생물의 정보 페이지로 이동
        st.link_button(
            f"📖 {creature['name']} 정보 알아보기",
            get_info_url(creature["name"]),
            use_container_width=True,
        )

        image_url = get_creature_image(creature["name"])
        if image_url:
            st.image(image_url, caption=creature["name"], width=350)


# =========================================================
# 9. 생물 도감
# =========================================================

elif page == "📚 생물 도감":
    st.header("📚 나의 생물 도감")
    st.write("발견한 생물과 아직 발견하지 못한 생물을 확인해 보세요.")

    col1, col2 = st.columns(2)

    with col1:
        category_options = ["전체"] + sorted(
            {creature["category"] for creature in SPECIES}
        )
        selected_category = st.selectbox("분류 필터", category_options)

    with col2:
        rarity_options = ["전체"] + RARITY_ORDER
        selected_rarity = st.selectbox("희귀도 필터", rarity_options)

    filtered_species = [
        creature for creature in SPECIES
        if (selected_category == "전체" or creature["category"] == selected_category)
        and (selected_rarity == "전체" or creature["rarity"] == selected_rarity)
    ]

    st.progress(
        len(st.session_state.discovered) / max(len(SPECIES), 1),
        text=f"도감 완성도: {len(st.session_state.discovered)}/{len(SPECIES)}"
    )

    columns = st.columns(3)

    for index, creature in enumerate(filtered_species):
        with columns[index % 3]:
            name = creature["name"]

            with st.container(border=True):
                if name in st.session_state.discovered:
                    st.subheader(f"{creature['emoji']} {name}")
                    st.caption(
                        f"{creature['category']} · "
                        f"{creature['rarity']} · "
                        f"{', '.join(creature['habitats'])}"
                    )
                    st.write(creature["description"])

                    st.link_button(
                        f"📖 {name} 정보 보기",
                        get_info_url(name),
                        key=f"info_{index}_{name}",
                        use_container_width=True,
                    )
                else:
                    st.subheader("❔ 미발견 생물")
                    st.write("아직 발견하지 못한 생물이에요.")
                    st.caption("탐험을 진행해 이 생물을 발견해 보세요!")


# =========================================================
# 10. 생물 퀴즈
# =========================================================

elif page == "🧠 생물 퀴즈":
    st.header("🧠 생물 퀴즈")
    st.write("설명을 읽고 어떤 생물인지 맞혀 보세요.")

    if st.button("🎲 새 퀴즈 출제", use_container_width=True):
        st.session_state.quiz_question = random.choice(QUIZZES)
        st.session_state.quiz_options = random.sample(
            SPECIES,
            min(3, len(SPECIES)),
        )

        question = st.session_state.quiz_question
        options = st.session_state.quiz_options

        if all(item["name"] != question["name"] for item in options):
            correct_creature = next(
                (item for item in SPECIES if item["name"] == question["name"]),
                None,
            )
            if correct_creature:
                options[-1] = correct_creature

        random.shuffle(options)
        st.session_state.quiz_answered = False
        st.session_state.quiz_feedback = ""

    if "quiz_question" not in st.session_state:
        st.info("새 퀴즈 출제 버튼을 눌러 시작하세요.")
    else:
        question = st.session_state.quiz_question
        options = st.session_state.quiz_options

        st.subheader("🔍 어떤 생물일까요?")
        st.write(f"**특징:** {question['description']}")
        st.write(f"**분류:** {question['category']}")
        st.write(f"**서식지:** {', '.join(question['habitats'])}")

        option_names = [item["name"] for item in options]

        answer = st.radio(
            "정답을 선택하세요.",
            option_names,
            key="quiz_answer_choice",
            disabled=st.session_state.get("quiz_answered", False),
        )

        if st.button(
            "정답 확인",
            type="primary",
            disabled=st.session_state.get("quiz_answered", False),
            use_container_width=True,
        ):
            st.session_state.quiz_total += 1
            st.session_state.quiz_answered = True

            if answer == question["name"]:
                st.session_state.quiz_correct += 1
                st.session_state.quiz_feedback = "correct"
                add_xp(10)
            else:
                st.session_state.quiz_feedback = "wrong"

        if st.session_state.get("quiz_answered", False):
            if st.session_state.quiz_feedback == "correct":
                st.success(f"🎉 정답입니다! {question['name']}이에요.")
            else:
                st.error(f"아쉽지만 정답은 **{question['name']}**이에요.")

            st.write(f"**설명:** {question['description']}")

            st.button(
                "다음 문제로 이동하려면 '새 퀴즈 출제'를 눌러 주세요.",
                disabled=True,
                use_container_width=True,
            )


# =========================================================
# 11. 업적
# =========================================================

elif page == "🏆 업적":
    st.header("🏆 탐험 업적")
    st.write("탐험을 하면서 다양한 목표를 달성해 보세요.")

    discovered_count = len(st.session_state.discovered)
    exploration_count = st.session_state.exploration_count
    correct_count = st.session_state.quiz_correct

    achievements = [
        {
            "name": "첫 발견",
            "description": "생물을 처음으로 발견하기",
            "condition": discovered_count >= 1,
            "emoji": "🌱",
        },
        {
            "name": "탐험가",
            "description": "탐험 5회 진행하기",
            "condition": exploration_count >= 5,
            "emoji": "🧭",
        },
        {
            "name": "생물 수집가",
            "description": "생물 10종 발견하기",
            "condition": discovered_count >= 10,
            "emoji": "📚",
        },
        {
            "name": "생물 전문가",
            "description": "생물 30종 발견하기",
            "condition": discovered_count >= 30,
            "emoji": "🔬",
        },
        {
            "name": "퀴즈 도전자",
            "description": "퀴즈 정답 5개 맞히기",
            "condition": correct_count >= 5,
            "emoji": "🧠",
        },
        {
            "name": "도감 완성",
            "description": "모든 생물 발견하기",
            "condition": discovered_count >= len(SPECIES),
            "emoji": "👑",
        },
    ]

    completed_count = sum(
        1 for achievement in achievements if achievement["condition"]
    )

    st.progress(
        completed_count / len(achievements),
        text=f"달성한 업적: {completed_count}/{len(achievements)}"
    )

    for achievement in achievements:
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])

            with col1:
                st.markdown(f"# {achievement['emoji']}")

            with col2:
                st.subheader(achievement["name"])
                st.write(achievement["description"])

                if achievement["condition"]:
                    st.success("달성 완료!")
                else:
                    st.caption("아직 달성하지 못했어요.")


# =========================================================
# 12. 하단 정보
# =========================================================

st.divider()
st.caption(
    "🌿 바이오 헌터 | 생물 탐험과 학습을 위한 교육용 게임"
)
