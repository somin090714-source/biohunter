import streamlit as st
import requests
import random
import json
import hashlib
from datetime import datetime

# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="바이오 헌터",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

RARITIES = {
    "일반":   {"weight": 58, "xp": 10, "color": "#87958D", "emoji": "🍃"},
    "고급":   {"weight": 25, "xp": 20, "color": "#4F9B70", "emoji": "🌱"},
    "희귀":   {"weight": 12, "xp": 40, "color": "#4285E8", "emoji": "💎"},
    "초희귀": {"weight": 4,  "xp": 80, "color": "#A66BE0", "emoji": "✨"},
    "전설":   {"weight": 1,  "xp": 150, "color": "#E5A92C", "emoji": "👑"},
}

HABITATS = {
    "숲": "🌲",
    "초원": "🌾",
    "습지": "🪷",
    "연못": "💧",
    "산": "⛰️",
    "바다": "🌊",
    "도시·정원": "🌻",
}

# =========================================================
# 2. 생물 도감 데이터 100종
# 형식: 한국어 이름|영어 이름|분류|서식지|희귀도|생물 특징
# =========================================================

RAW_SPECIES = """
개구리|Frog|양서류|숲,습지,연못|일반|피부를 통해서도 수분과 기체를 교환할 수 있어요.
두꺼비|Toad|양서류|숲,초원|일반|건조한 환경에도 비교적 잘 적응하는 양서류예요.
청개구리|Japanese tree frog|양서류|숲,습지|고급|나무나 풀을 잘 타고 오를 수 있어요.
도롱뇽|Salamander|양서류|숲,습지|고급|일부 종은 손상된 신체 조직을 재생할 수 있어요.
무당개구리|Fire-bellied toad|양서류|습지,연못|고급|위험을 느끼면 선명한 배 색을 드러내요.
맹꽁이|Asian narrow-mouthed toad|양서류|습지,초원|희귀|땅속에서 생활하는 시간이 긴 편이에요.
산개구리|Brown frog|양서류|산,숲|고급|추운 계절에도 살아남을 수 있도록 적응했어요.
황소개구리|American bullfrog|양서류|연못,습지|일반|몸집이 크고 다양한 먹이를 먹어요.
아홀로틀|Axolotl|양서류|연못|초희귀|성체가 되어서도 유생의 특징을 유지해요.
유리개구리|Glass frog|양서류|숲|전설|일부 종은 배 쪽 피부가 투명해 내부 기관이 보여요.
고양이|Cat|포유류|도시·정원|일반|수염으로 주변의 좁은 공간을 감지하는 데 도움을 받아요.
강아지|Dog|포유류|도시·정원|일반|후각이 발달해 냄새를 구별하는 능력이 뛰어나요.
여우|Red fox|포유류|숲,초원|고급|청각과 후각을 이용해 먹이를 찾아요.
늑대|Wolf|포유류|숲,산|희귀|무리를 이루어 협력하는 행동을 보여요.
호랑이|Tiger|포유류|숲|초희귀|줄무늬 무늬가 개체를 구별하는 특징 중 하나예요.
사자|Lion|포유류|초원|초희귀|사회적 무리를 이루어 생활하는 대표적인 고양잇과 동물이에요.
코끼리|Elephant|포유류|초원|희귀|긴 코를 이용해 물을 마시고 물체를 다뤄요.
기린|Giraffe|포유류|초원|희귀|긴 목으로 높은 곳의 잎을 먹을 수 있어요.
판다|Giant panda|포유류|숲|초희귀|주로 대나무를 먹지만 소화기관은 육식동물과 비슷한 점이 있어요.
수달|Otter|포유류|습지,연못,바다|희귀|물속 생활에 적응한 몸과 발을 가지고 있어요.
고슴도치|Hedgehog|포유류|숲,도시·정원|고급|위협을 느끼면 몸을 웅크려 가시로 자신을 보호해요.
박쥐|Bat|포유류|숲,도시·정원|희귀|많은 종이 반향정위를 이용해 주변을 파악해요.
고래|Whale|포유류|바다|초희귀|폐로 호흡하기 때문에 주기적으로 수면 위로 올라와요.
돌고래|Dolphin|포유류|바다|희귀|소리와 반향정위를 이용해 먹이와 주변 환경을 파악해요.
북극곰|Polar bear|포유류|산,바다|전설|두꺼운 지방층과 털이 추운 환경에서 체온을 유지하도록 도와요.
다람쥐|Squirrel|포유류|숲|일반|먹이를 저장하고 일부를 잊어버려 식물의 씨앗 확산에 기여해요.
고라니|Water deer|포유류|숲,습지|고급|한국에서도 볼 수 있는 초식성 포유류예요.
사슴|Deer|포유류|숲,산|고급|많은 종에서 수컷의 뿔이 해마다 새로 자라요.
오랑우탄|Orangutan|포유류|숲|초희귀|나무 위 생활에 적응한 긴 팔을 가지고 있어요.
나무늘보|Sloth|포유류|숲|희귀|에너지를 아끼는 느린 움직임으로 알려져 있어요.
참새|Eurasian tree sparrow|조류|도시·정원,초원|일반|도시와 농촌 주변에서 쉽게 관찰되는 새예요.
까치|Oriental magpie|조류|도시·정원,숲|일반|여러 환경에 적응해 살아가는 새예요.
비둘기|Rock pigeon|조류|도시·정원|일반|도시 환경에서 먹이를 찾는 능력이 뛰어나요.
까마귀|Crow|조류|숲,도시·정원|고급|문제 해결과 도구 사용 행동이 관찰돼요.
독수리|Eagle|조류|산|희귀|날카로운 발톱과 부리로 먹이를 잡아요.
매|Falcon|조류|산,도시·정원|희귀|빠른 비행과 시각을 이용해 먹이를 사냥해요.
펭귄|Penguin|조류|바다|희귀|날개가 물속에서 추진력을 내는 지느러미처럼 변했어요.
타조|Ostrich|조류|초원|고급|현존하는 새 중 가장 큰 종이며 잘 달려요.
공작|Peacock|조류|숲|희귀|화려한 깃털은 짝짓기 행동과 관련이 있어요.
올빼미|Owl|조류|숲|고급|어두운 환경에서 먹이를 찾는 데 특화되어 있어요.
두루미|Crane|조류|습지|초희귀|습지 생태계와 관련이 깊은 큰 새예요.
황새|Oriental stork|조류|습지|희귀|얕은 물에서 물고기와 작은 동물을 찾아요.
백로|Egret|조류|습지,연못|고급|긴 다리로 물가를 걸으며 먹이를 찾아요.
벌새|Hummingbird|조류|숲|전설|공중에서 정지 비행하며 꽃의 꿀을 먹을 수 있어요.
알바트로스|Albatross|조류|바다|초희귀|긴 날개를 이용해 바다 위를 효율적으로 활공해요.
오리|Duck|조류|연못,습지|일반|물갈퀴가 수영할 때 도움을 줘요.
딱따구리|Woodpecker|조류|숲|고급|단단한 부리로 나무를 쪼아 먹이를 찾아요.
제비|Swallow|조류|도시·정원,초원|고급|날면서 곤충을 잡아먹는 능력이 뛰어나요.
앵무새|Parrot|조류|숲|희귀|일부 종은 소리를 모방하는 능력을 보여요.
수리부엉이|Eurasian eagle-owl|조류|산,숲|초희귀|큰 눈과 예민한 청각으로 먹이를 찾아요.
금붕어|Goldfish|어류|연못|일반|아가미로 물속의 용존 산소를 흡수해요.
잉어|Common carp|어류|연못,습지|일반|바닥의 먹이를 찾는 데 입 주변의 감각기관을 이용해요.
연어|Salmon|어류|바다,연못|희귀|일부 종은 번식할 때 태어난 하천으로 돌아와요.
흰동가리|Clownfish|어류|바다|고급|말미잘과 상호작용하며 살아가는 것으로 유명해요.
상어|Shark|어류|바다|희귀|연골로 이루어진 골격을 가지고 있어요.
가오리|Stingray|어류|바다|고급|넓고 납작한 몸으로 물속을 헤엄쳐요.
해마|Seahorse|어류|바다|초희귀|수컷이 알을 품는 육아 주머니를 가진 종이 있어요.
참치|Tuna|어류|바다|고급|유선형 몸으로 빠르게 헤엄칠 수 있어요.
복어|Pufferfish|어류|바다|희귀|위협을 받으면 몸을 부풀리는 종이 있어요.
송사리|Medaka|어류|연못,습지|일반|작고 관찰하기 쉬워 생물 연구에 활용돼요.
철갑상어|Sturgeon|어류|바다,연못|초희귀|오랜 진화 역사를 가진 어류 집단이에요.
흰수마자|White river sturgeon|어류|연못|전설|일부 철갑상어류는 장수하는 것으로 알려져 있어요.
무지개송어|Rainbow trout|어류|산,연못|고급|차가운 물과 산소가 풍부한 환경에서 잘 살아가요.
피라냐|Piranha|어류|연못|희귀|강한 턱과 이빨을 가진 종들이 있어요.
개복치|Ocean sunfish|어류|바다|초희귀|몸이 높고 납작한 독특한 형태를 가지고 있어요.
장어|Eel|어류|연못,바다|희귀|뱀처럼 긴 몸으로 좁은 공간을 이동할 수 있어요.
도마뱀|Lizard|파충류|숲,산|일반|변온동물로 외부 환경에 따라 체온이 달라져요.
거북|Turtle|파충류|연못,바다|고급|단단한 등딱지가 몸을 보호해요.
악어|Crocodile|파충류|습지|희귀|눈과 콧구멍이 머리 위쪽에 있어 물속에서 유리해요.
카멜레온|Chameleon|파충류|숲|초희귀|독립적으로 움직이는 눈과 긴 혀가 특징이에요.
이구아나|Iguana|파충류|숲|고급|많은 종이 식물성 먹이를 주로 먹어요.
코브라|Cobra|파충류|초원,숲|희귀|위협을 느끼면 목 주변을 펼치는 종이 있어요.
왕도마뱀|Monitor lizard|파충류|초원|희귀|혀를 이용해 주변의 화학적 신호를 감지해요.
바다거북|Sea turtle|파충류|바다|초희귀|알을 낳기 위해 모래 해변으로 올라오는 종이 있어요.
살모사|Viper|파충류|산,숲|고급|독을 이용해 먹이를 사냥하는 종이에요.
비단뱀|Python|파충류|숲|초희귀|먹이를 몸으로 감싸 압박하는 종이 있어요.
꿀벌|Honey bee|곤충|숲,초원,도시·정원|일반|꽃가루받이를 도와 식물의 번식에 기여해요.
나비|Butterfly|곤충|숲,초원,도시·정원|일반|애벌레와 성충의 먹이가 다른 경우가 많아요.
무당벌레|Ladybird|곤충|초원,도시·정원|일반|진딧물을 먹는 종이 있어 농업에 도움이 돼요.
반딧불이|Firefly|곤충|습지,숲|희귀|화학 반응을 통해 빛을 내는 생물이에요.
사마귀|Praying mantis|곤충|초원,숲|고급|앞다리를 이용해 먹이를 붙잡아요.
장수풍뎅이|Japanese rhinoceros beetle|곤충|숲|희귀|수컷의 뿔은 경쟁 행동에 사용돼요.
사슴벌레|Stag beetle|곤충|숲|희귀|큰 턱을 이용해 다른 개체와 경쟁하기도 해요.
잠자리|Dragonfly|곤충|습지,연못|고급|날개를 독립적으로 움직여 방향을 바꿀 수 있어요.
개미|Ant|곤충|숲,도시·정원|일반|화학적 신호를 이용해 동료와 정보를 주고받아요.
매미|Cicada|곤충|숲,도시·정원|일반|수컷은 소리를 내어 짝을 찾는 행동을 해요.
대벌레|Stick insect|곤충|숲|희귀|식물의 줄기처럼 보이는 위장 형태를 가져요.
물장군|Giant water bug|곤충|습지,연못|초희귀|물속에서 사냥하는 대형 수서곤충이에요.
왕나비|Monarch butterfly|곤충|초원,도시·정원|초희귀|장거리 이동 행동으로 잘 알려져 있어요.
누에나방|Silkworm moth|곤충|숲|고급|애벌레가 만드는 실크는 섬유 생산에 활용돼요.
풀잠자리|Lacewing|곤충|초원,도시·정원|고급|유충이 작은 해충을 잡아먹기도 해요.
소나무|Pine tree|식물|산,숲|일반|씨앗이 열매가 아닌 솔방울 안에서 발달해요.
은행나무|Ginkgo|식물|도시·정원,산|희귀|살아 있는 화석이라고 불릴 만큼 오래된 계통이에요.
해바라기|Sunflower|식물|초원,도시·정원|일반|꽃의 구조가 많은 작은 꽃으로 이루어져 있어요.
민들레|Dandelion|식물|초원,도시·정원|일반|씨앗이 바람을 타고 퍼지기 쉬운 구조예요.
선인장|Cactus|식물|초원|고급|잎이 가시로 변해 수분 손실을 줄이는 데 도움을 줘요.
연꽃|Lotus|식물|연못,습지|고급|잎 표면의 특성 때문에 물방울이 쉽게 굴러가요.
파리지옥|Venus flytrap|식물|습지|희귀|곤충이 닿으면 잎을 닫아 먹이를 붙잡아요.
네펜데스|Tropical pitcher plant|식물|숲|초희귀|항아리 모양 잎으로 작은 동물을 잡는 종이 있어요.
세쿼이아|Giant sequoia|식물|숲,산|전설|매우 크게 자라고 오래 사는 나무로 알려져 있어요.
이끼|Moss|식물|숲,산,습지|일반|관다발 조직이 발달한 식물과 달리 작고 습한 곳에서 잘 자라요.
"""

def load_species():
    result = []
    for i, line in enumerate(RAW_SPECIES.strip().splitlines(), start=1):
        parts = line.split("|")
        if len(parts) != 6:
            continue
        name, english, group, habitats, rarity, fact = parts
        result.append({
            "id": f"sp_{i:03d}",
            "name": name,
            "english": english,
            "group": group,
            "habitats": habitats.split(","),
            "rarity": rarity,
            "fact": fact,
        })
    return result

SPECIES = load_species()
SPECIES_BY_ID = {s["id"]: s for s in SPECIES}
GROUPS = sorted(set(s["group"] for s in SPECIES))

# =========================================================
# 3. 생명과학 퀴즈
# 형식: 문제, 선택지, 정답 번호, 해설
# =========================================================

QUIZZES = {
    "쉬움": [
        ("세포에서 유전 정보를 주로 저장하는 물질은?", ["단백질", "DNA", "지방", "녹말"], 1,
         "DNA는 유전 정보를 저장하는 핵심 물질이에요."),
        ("식물이 광합성할 때 주로 흡수하는 기체는?", ["산소", "질소", "이산화탄소", "수소"], 2,
         "식물은 이산화탄소와 물을 이용해 유기물을 만들어요."),
        ("세포에서 에너지를 얻는 세포 호흡이 주로 일어나는 곳은?", ["미토콘드리아", "리보솜", "핵", "세포벽"], 0,
         "미토콘드리아는 세포 호흡과 ATP 생산에 중요한 역할을 해요."),
        ("효소의 주된 역할은?", ["유전 정보 저장", "반응 속도 증가", "세포막 형성만 담당", "산소 생성"], 1,
         "효소는 활성화 에너지를 낮춰 화학 반응을 빠르게 해요."),
        ("동물 세포와 식물 세포에 공통으로 있는 구조는?", ["세포벽", "엽록체", "세포막", "큰 액포만"], 2,
         "세포막은 동물 세포와 식물 세포 모두에 있어요."),
        ("먹이사슬에서 식물의 일반적인 역할은?", ["분해자", "생산자", "최상위 포식자", "기생자"], 1,
         "식물은 광합성으로 유기물을 만드는 생산자예요."),
        ("생물의 몸에서 유전 정보를 다음 세대로 전달하는 과정과 가장 관련 깊은 것은?", ["번식", "증발", "풍화", "응결"], 0,
         "번식은 유전 정보를 다음 세대로 전달하는 과정이에요."),
        ("아가미를 가진 물고기가 물에서 얻는 기체는?", ["이산화탄소만", "산소", "수소", "헬륨"], 1,
         "물고기는 아가미에서 물에 녹아 있는 산소를 흡수해요."),
        ("생물의 몸을 이루는 기본 구조적 단위는?", ["기관계", "기관", "세포", "개체군"], 2,
         "세포는 생물의 기본 구조적·기능적 단위예요."),
        ("꽃가루가 암술머리에 도달하는 과정은?", ["수정", "수분", "발아", "호흡"], 1,
         "수분은 꽃가루가 암술머리에 옮겨지는 과정이에요."),
        ("생태계에서 죽은 생물을 분해하는 역할을 하는 생물의 예는?", ["곰팡이", "사슴", "소나무", "매"], 0,
         "곰팡이와 많은 세균은 유기물을 분해해 물질 순환에 기여해요."),
        ("DNA의 기본 단위는?", ["아미노산", "뉴클레오타이드", "지방산", "포도당"], 1,
         "DNA는 뉴클레오타이드가 연결된 분자예요."),
    ],
    "보통": [
        ("효소 반응에서 온도가 지나치게 높아졌을 때 반응 속도가 감소할 수 있는 주된 이유는?",
         ["기질이 원소로 분해되기 때문", "효소의 입체 구조가 변할 수 있기 때문",
          "효소가 항상 얼기 때문", "반응에 물이 없어지기 때문"], 1,
         "높은 온도는 효소의 구조를 변화시켜 활성 부위의 모양에 영향을 줄 수 있어요."),
        ("제한 효소가 유전자 재조합 기술에 이용되는 핵심 이유는?",
         ["DNA를 무작위로 복제하기 때문", "특정 염기서열을 인식해 DNA를 자르기 때문",
          "단백질을 직접 합성하기 때문", "세포막을 녹이기 때문"], 1,
         "제한 효소는 특정 DNA 서열을 인식하고 절단해 유전자 조작에 활용돼요."),
        ("세포막이 물질의 이동을 선택적으로 조절할 수 있는 이유와 가장 관련 깊은 것은?",
         ["모든 물질이 자유롭게 통과하기 때문", "인지질 이중층과 막단백질의 특성",
          "세포막이 단단한 세포벽이기 때문", "DNA가 막을 이루기 때문"], 1,
         "인지질 이중층과 막단백질은 물질의 종류에 따라 이동을 조절해요."),
        ("DNA 복제에서 상보적인 염기쌍을 이루는 것은?",
         ["A-G, T-C", "A-T, G-C", "A-C, G-T", "A-A, G-G"], 1,
         "DNA에서는 아데닌(A)-티민(T), 구아닌(G)-사이토신(C)이 짝을 이뤄요."),
        ("광합성의 명반응에서 직접 생성되는 에너지 전달 물질 조합은?",
         ["ATP와 NADPH", "DNA와 RNA", "젖산과 에탄올", "요소와 암모니아"], 0,
         "명반응은 ATP와 NADPH를 만들어 탄소 고정에 필요한 에너지를 제공해요."),
        ("개체군의 크기가 환경 수용력에 가까워질 때 나타날 수 있는 현상은?",
         ["자원이 무한히 증가함", "개체군 증가 속도가 느려짐",
          "모든 개체가 즉시 사라짐", "돌연변이가 완전히 멈춤"], 1,
         "먹이와 공간 같은 자원이 제한되면 개체군 증가가 둔화될 수 있어요."),
        ("항생제 내성 세균이 집단에서 증가하는 현상을 가장 잘 설명하는 것은?",
         ["세균이 필요할 때 내성을 의도적으로 만듦", "항생제가 내성 없는 세균을 더 많이 제거함",
          "모든 세균이 같은 돌연변이를 가짐", "항생제가 세균의 DNA를 항상 복구함"], 1,
         "항생제에 살아남은 내성 세균이 번식하면서 내성 비율이 높아질 수 있어요."),
        ("삼투 현상을 가장 잘 설명한 것은?",
         ["용질이 막을 통해 항상 고농도에서 저농도로 이동함",
          "물 분자가 선택적 투과막을 통해 이동함",
          "단백질이 DNA로 바뀜", "ATP가 유전자로 변함"], 1,
         "삼투는 선택적 투과막을 사이에 둔 물의 이동이에요."),
        ("유전자 발현에서 전사에 해당하는 과정은?",
         ["DNA 정보를 RNA로 옮김", "RNA 정보를 단백질로 번역함",
          "단백질을 DNA로 바꿈", "포도당을 ATP로 바꿈"], 0,
         "전사는 DNA 정보를 바탕으로 RNA를 합성하는 과정이에요."),
        ("생물 다양성이 생태계에 중요한 이유로 가장 적절한 것은?",
         ["생태계의 모든 변화가 사라지기 때문", "생태계 기능과 환경 변화에 대한 대응에 기여하기 때문",
          "먹이 관계가 없어지기 때문", "모든 종의 유전자가 같아지기 때문"], 1,
         "다양한 종과 유전적 차이는 생태계의 기능과 변화 대응에 중요해요."),
        ("경쟁 배타 원리에 대한 설명으로 가장 적절한 것은?",
         ["같은 자원을 완전히 똑같이 쓰는 종은 언제나 공존함",
          "생태적 지위가 매우 겹치는 종 사이에서 한 종이 밀려날 수 있음",
          "모든 종은 같은 먹이만 먹음", "경쟁은 생태계에서 일어나지 않음"], 1,
         "자원 이용이 크게 겹치면 경쟁으로 인해 한 종의 생존이 불리해질 수 있어요."),
        ("미토콘드리아에서 산소가 필요한 세포 호흡 과정과 관련 깊은 것은?",
         ["전자 전달계", "DNA 전사만", "광계 II", "질소 고정만"], 0,
         "산소는 미토콘드리아 전자 전달계에서 최종 전자 수용체로 작용해요."),
    ],
    "어려움": [
        ("제한 효소로 잘린 DNA 조각을 벡터에 연결하는 데 직접 관여하는 효소는?",
         ["DNA 연결 효소(ligase)", "아밀레이스", "펩신", "카탈레이스"], 0,
         "DNA 연결 효소는 DNA 조각 사이에 인산다이에스터 결합이 형성되도록 도와요."),
        ("서로 다른 DNA를 같은 제한 효소로 절단했을 때 끈끈한 말단이 생길 수 있는 이유는?",
         ["절단 위치가 어긋나 단일 가닥 돌출부가 생길 수 있기 때문",
          "DNA가 단백질로 변하기 때문", "염기가 모두 제거되기 때문",
          "DNA가 세포막으로 변하기 때문"], 0,
         "엇갈린 절단은 상보적인 염기쌍을 이룰 수 있는 단일 가닥 돌출부를 만들 수 있어요."),
        ("PCR에서 프라이머의 주된 역할은?",
         ["DNA 합성이 시작될 위치를 제공함", "DNA를 단백질로 바꿈",
          "DNA를 무작위로 자름", "세포를 직접 분열시킴"], 0,
         "프라이머는 DNA 중합효소가 합성을 시작할 수 있도록 표적 영역의 양 끝에 결합해요."),
        ("유전자 재조합에서 플라스미드를 벡터로 사용하는 이유로 가장 적절한 것은?",
         ["세포 안에서 복제될 수 있고 외래 DNA를 운반할 수 있기 때문",
          "항상 사람의 염색체와 같기 때문", "단백질만 저장하기 때문",
          "세포막을 없애기 때문"], 0,
         "플라스미드는 외래 유전자를 숙주 세포로 운반하는 벡터로 활용될 수 있어요."),
        ("열성 유전 형질이 표현형으로 나타나는 일반적인 조건은?",
         ["열성 대립유전자가 하나만 있어도 항상 발현", "열성 대립유전자가 두 개 있는 경우",
          "염색체가 없을 때만 발현", "환경과 무관하게 모든 사람에게 발현"], 1,
         "단순한 완전 우성 관계에서는 열성 대립유전자 두 개일 때 열성 형질이 나타나요."),
        ("어떤 효소의 활성 부위에 기질과 유사한 물질이 결합해 반응을 억제한다. 가장 알맞은 설명은?",
         ["경쟁적 저해", "비경쟁적 저해만", "삼투", "DNA 복제"], 0,
         "경쟁적 저해제는 기질과 활성 부위 결합을 두고 경쟁해요."),
        ("유전자 발현량을 비교할 때 대조군과 실험군을 함께 두는 중요한 이유는?",
         ["모든 결과를 같게 만들기 위해", "처리 효과와 다른 요인의 영향을 구분하기 위해",
          "유전자를 없애기 위해", "표본 수를 무조건 줄이기 위해"], 1,
         "대조군은 실험 처리에 따른 차이를 해석하는 기준이 돼요."),
        ("생태계에서 특정 포식자가 사라진 뒤 초식동물이 크게 늘어 식물이 감소했다. 이는 무엇의 예인가?",
         ["먹이그물의 연쇄적 변화", "유전자 복제", "삼투압의 일정한 유지", "단백질 번역"], 0,
         "먹이 관계의 한 변화가 여러 영양 단계에 연쇄적으로 영향을 줄 수 있어요."),
        ("유전적 부동의 영향이 상대적으로 크게 나타나기 쉬운 집단은?",
         ["개체 수가 매우 큰 집단", "개체 수가 작은 집단",
          "유전적 변화가 절대 없는 집단", "번식하지 않는 집단만"], 1,
         "작은 집단에서는 우연한 사건이 대립유전자 빈도에 큰 영향을 줄 수 있어요."),
        ("어떤 DNA 표본에서 특정 유전자의 발현량을 RNA 수준에서 비교하려 한다. 적절한 방법은?",
         ["역전사 후 실시간 PCR", "단순한 광합성 측정", "삼투압만 측정",
          "현미경으로 세포 크기만 비교"], 0,
         "RNA를 cDNA로 바꾼 뒤 실시간 PCR로 발현량을 비교할 수 있어요."),
        ("같은 종의 개체 사이에 유전적 다양성이 존재하면 환경 변화에서 유리할 수 있는 이유는?",
         ["모든 개체가 같은 반응을 하기 때문", "일부 개체가 새로운 환경에 더 잘 적응할 가능성이 있기 때문",
          "돌연변이가 완전히 사라지기 때문", "자연선택이 멈추기 때문"], 1,
         "유전적 다양성은 환경 변화에 적합한 형질을 가진 개체가 존재할 가능성을 높여요."),
        ("효소의 반응 속도를 기질 농도에 따라 측정했을 때 높은 농도에서 속도가 거의 일정해졌다. 가장 적절한 설명은?",
         ["효소의 활성 부위가 대부분 기질로 채워졌기 때문",
          "모든 기질이 사라졌기 때문", "효소가 무한히 증가했기 때문",
          "반응이 물리적으로 불가능해졌기 때문"], 0,
         "효소의 활성 부위가 기질로 포화되면 기질 농도를 높여도 속도 증가가 제한돼요."),
    ],
}

# =========================================================
# 4. 게임 화면 디자인
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background:
      radial-gradient(ellipse at top left, rgba(188,225,181,.55), transparent 42%),
      radial-gradient(ellipse at bottom right, rgba(248,219,155,.55), transparent 40%),
      linear-gradient(140deg, #f4f8e9 0%, #e4f0df 48%, #f8f0d9 100%);
}
.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: 'Jua', sans-serif !important;
    color: #244d3b;
}
.hero {
    background: linear-gradient(120deg, #234d3b, #397456);
    border: 2px solid rgba(255,255,255,.55);
    border-radius: 26px;
    padding: 25px 28px;
    color: white;
    box-shadow: 0 10px 25px rgba(37,75,53,.18);
    margin-bottom: 18px;
}
.hero h1 { color: #fff7d7; font-size: 2.6rem; margin: 0; }
.hero p { color: #e6f5df; margin-bottom: 0; }
.panel {
    background: rgba(255,255,255,.83);
    border: 1px solid #d7e6d2;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 5px 16px rgba(38,76,48,.07);
    margin-bottom: 12px;
}
.small-note { color: #63786b; font-size: .9rem; }
.tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 99px;
    background: #e6efe0;
    color: #315c43;
    font-size: .82rem;
    font-weight: 700;
    margin: 2px;
}
div.stButton > button {
    border-radius: 13px;
    border: 1px solid #bed4b7;
    background: linear-gradient(135deg, #fffef6, #e8f3e2);
    color: #28513a;
    font-weight: 800;
    min-height: 44px;
    transition: .15s ease;
}
div.stButton > button:hover {
    border-color: #548565;
    color: #1d4c32;
    transform: translateY(-1px);
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,.82);
    border: 1px solid #d7e6d2;
    border-radius: 17px;
    padding: 13px 16px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e1efd9, #f7f0d9);
}
hr { border-color: #d6e5d1; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 5. Supabase 저장 함수
# =========================================================

def get_supabase_config():
    try:
        url = st.secrets["SUPABASE_URL"].rstrip("/")
        key = st.secrets["SUPABASE_KEY"]
        return url, key
    except Exception:
        return None, None

def db_headers():
    url, key = get_supabase_config()
    if not url or not key:
        return None, None
    return url, {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

def load_save(save_code):
    url, headers = db_headers()
    if not url:
        return None, "Supabase Secrets 설정이 필요합니다."

    try:
        response = requests.get(
            f"{url}/rest/v1/game_saves",
            headers=headers,
            params={
                "save_code": f"eq.{save_code}",
                "select": "save_data",
                "limit": 1,
            },
            timeout=10,
        )
        if response.status_code >= 400:
            return None, f"데이터 불러오기 오류: {response.status_code}"
        rows = response.json()
        if rows:
            return rows[0]["save_data"], None
        return {}, None
    except Exception as e:
        return None, f"연결 오류: {e}"

def save_game():
    if not st.session_state.get("save_code"):
        return False
    url, headers = db_headers()
    if not url:
        return False

    payload = {
        "save_code": st.session_state.save_code,
        "save_data": {
            "collection": st.session_state.collection,
            "xp": st.session_state.xp,
            "found_total": st.session_state.found_total,
            "quiz_correct": st.session_state.quiz_correct,
            "quiz_total": st.session_state.quiz_total,
            "discovery_log": st.session_state.discovery_log[-30:],
            "last_found": st.session_state.last_found,
            "last_saved": datetime.now().isoformat(timespec="seconds"),
        },
    }

    try:
        response = requests.post(
            f"{url}/rest/v1/game_saves?on_conflict=save_code",
            headers={**headers, "Prefer": "resolution=merge-duplicates,return=minimal"},
            json=payload,
            timeout=10,
        )
        return response.status_code < 400
    except Exception:
        return False

# =========================================================
# 6. 초기화 및 로그인(저장 코드)
# =========================================================

if "save_code" not in st.session_state:
    st.session_state.save_code = ""
if "loaded" not in st.session_state:
    st.session_state.loaded = False
if "collection" not in st.session_state:
    st.session_state.collection = {}
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "found_total" not in st.session_state:
    st.session_state.found_total = 0
if "quiz_correct" not in st.session_state:
    st.session_state.quiz_correct = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0
if "discovery_log" not in st.session_state:
    st.session_state.discovery_log = []
if "last_found" not in st.session_state:
    st.session_state.last_found = None
if "quiz_question" not in st.session_state:
    st.session_state.quiz_question = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

def reset_progress():
    st.session_state.collection = {}
    st.session_state.xp = 0
    st.session_state.found_total = 0
    st.session_state.quiz_correct = 0
    st.session_state.quiz_total = 0
    st.session_state.discovery_log = []
    st.session_state.last_found = None
    st.session_state.quiz_question = None
    st.session_state.quiz_answered = False
    st.session_state.quiz_result = None

# 저장 코드 입력 화면
if not st.session_state.loaded:
    st.markdown("""
    <div class="hero">
      <h1>🌿 바이오 헌터</h1>
      <p>탐험하고, 발견하고, 생명과학 지식을 키워 보세요!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔐 나의 탐험 기록")
    st.write("처음 이용한다면 새 저장 코드를 만들고, 다시 방문했다면 기존 코드를 입력하세요.")
    st.caption("저장 코드는 계정 비밀번호처럼 안전하게 보관하세요. 다른 사람과 공유하면 기록에 접근할 수 있습니다.")

    with st.form("load_form"):
        code = st.text_input(
            "저장 코드",
            placeholder="예: forest-2026",
            max_chars=40,
        )
        submit = st.form_submit_button("탐험 시작하기", use_container_width=True)

    if submit:
        cleaned = code.strip()
        if len(cleaned) < 4:
            st.error("저장 코드는 4글자 이상 입력해 주세요.")
        elif not all(c.isalnum() or c in "-_" for c in cleaned):
            st.error("저장 코드는 영문자, 숫자, 하이픈(-), 밑줄(_)만 사용할 수 있어요.")
        else:
            data, error = load_save(cleaned)
            if error:
                st.error(error)
                st.info("Supabase 프로젝트와 Streamlit Secrets 설정을 확인해 주세요.")
            else:
                st.session_state.save_code = cleaned
                reset_progress()
                if data:
                    st.session_state.collection = data.get("collection", {})
                    st.session_state.xp = int(data.get("xp", 0))
                    st.session_state.found_total = int(data.get("found_total", 0))
                    st.session_state.quiz_correct = int(data.get("quiz_correct", 0))
                    st.session_state.quiz_total = int(data.get("quiz_total", 0))
                    st.session_state.discovery_log = data.get("discovery_log", [])
                    st.session_state.last_found = data.get("last_found")
                    st.success("이전 탐험 기록을 불러왔어요!")
                else:
                    st.info("새로운 탐험 기록을 만들었어요!")
                st.session_state.loaded = True
                st.rerun()
    st.stop()

# =========================================================
# 7. 레벨과 경험치
# =========================================================

def get_level(xp):
    level = 1
    remaining = xp
    while remaining >= level * 100:
        remaining -= level * 100
        level += 1
    return level, remaining, level * 100

level, level_xp, next_xp = get_level(st.session_state.xp)

# =========================================================
# 8. 사진 가져오기
# =========================================================

@st.cache_data(ttl=86400, show_spinner=False)
def get_species_photo(english_name):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(english_name)}"
        response = requests.get(
            url,
            headers={"User-Agent": "BioHunter/1.0 educational project"},
            timeout=6,
        )
        if response.status_code == 200:
            data = response.json()
            image = data.get("thumbnail", {}).get("source")
            page = data.get("content_urls", {}).get("desktop", {}).get("page")
            return image, page
    except Exception:
        pass
    return None, None

def display_photo(species, width=220):
    image, page = get_species_photo(species["english"])
    if image:
        st.image(image, width=width)
        if page:
            st.caption(f"사진 및 참고 자료: [Wikipedia]({page})")
    else:
        st.markdown(
            "<div style='font-size:4rem;text-align:center;padding:15px;'>🌿</div>",
            unsafe_allow_html=True,
        )
        st.caption("사진을 불러오지 못했어요. 인터넷 연결을 확인해 주세요.")

# =========================================================
# 9. 생물 발견 로직
# =========================================================

def discover_species(habitat):
    candidates = [s for s in SPECIES if habitat in s["habitats"]]
    if not candidates:
        st.warning("이 서식지에서 발견할 생물이 없어요.")
        return

    # 기본 희귀도 확률: 일반 58, 고급 25, 희귀 12, 초희귀 4, 전설 1
    # 미발견 생물은 발견 확률을 높여 도감 수집을 돕는다.
    weighted = []
    weights = []
    for species in candidates:
        base = RARITIES[species["rarity"]]["weight"]
        already_found = species["id"] in st.session_state.collection
        multiplier = 0.35 if already_found else 2.8
        weighted.append(species)
        weights.append(base * multiplier)

    found = random.choices(weighted, weights=weights, k=1)[0]
    is_new = found["id"] not in st.session_state.collection

    if is_new:
        reward = RARITIES[found["rarity"]]["xp"]
        st.session_state.collection[found["id"]] = 1
        st.session_state.xp += reward
        message = f"새 생물 발견! 경험치 +{reward}"
    else:
        st.session_state.collection[found["id"]] += 1
        reward = 3
        st.session_state.xp += reward
        message = f"중복 발견! 경험치 +{reward}"

    st.session_state.found_total += 1
    st.session_state.last_found = found["id"]
    st.session_state.discovery_log.append({
        "name": found["name"],
        "rarity": found["rarity"],
        "habitat": habitat,
        "new": is_new,
        "time": datetime.now().strftime("%m-%d %H:%M"),
    })
    st.session_state.discovery_log = st.session_state.discovery_log[-30:]
    save_game()
    return found, is_new, message

# =========================================================
# 10. 상단 게임 정보
# =========================================================

st.markdown(f"""
<div class="hero">
  <h1>🌿 바이오 헌터</h1>
  <p>자연 속 생물을 발견하고, 나만의 생태 도감을 완성하세요.</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("🧭 탐험 레벨", f"Lv. {level}")
m2.metric("📚 도감 완성도", f"{len(st.session_state.collection)} / {len(SPECIES)}")
m3.metric("✨ 누적 경험치", f"{st.session_state.xp:,} XP")
m4.metric("🔎 총 발견 횟수", f"{st.session_state.found_total:,}")

st.progress(min(level_xp / next_xp, 1.0))
st.caption(f"다음 레벨까지 {next_xp - level_xp} XP 남았어요!")

st.sidebar.markdown("## 🌱 탐험 메뉴")
st.sidebar.markdown(f"**Lv. {level} 탐험가**")
st.sidebar.progress(min(level_xp / next_xp, 1.0))
st.sidebar.caption(f"도감 {len(st.session_state.collection)} / {len(SPECIES)}종")

page = st.sidebar.radio(
    "이동할 곳",
    ["🧭 탐험하기", "📖 생물 도감", "🧪 생명과학 퀴즈", "🏆 업적", "⚙️ 설정"],
)

# =========================================================
# 11. 탐험 페이지
# =========================================================

if page == "🧭 탐험하기":
    st.markdown("## 🧭 자연 탐험")
    st.write("탐험할 서식지를 선택한 뒤 생물 발견 버튼을 눌러 보세요.")

    cols = st.columns(4)
    habitat_names = list(HABITATS.keys())
    for i, habitat in enumerate(habitat_names):
        with cols[i % 4]:
            count = sum(
                1 for s in SPECIES
                if habitat in s["habitats"] and s["id"] in st.session_state.collection
            )
            total = sum(1 for s in SPECIES if habitat in s["habitats"])
            st.markdown(
                f"""<div class="panel" style="text-align:center;">
                <div style="font-size:2.3rem;">{HABITATS[habitat]}</div>
                <b>{habitat}</b><br>
                <span class="small-note">도감 {count}/{total}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    habitat = st.selectbox("탐험할 서식지", list(HABITATS.keys()))
    st.markdown(
        f"""<div class="panel">
        <h3>{HABITATS[habitat]} {habitat} 탐험 구역</h3>
        <p>이 지역에 서식하는 생물 중 하나를 무작위로 발견해요.</p>
        <span class="tag">미발견 생물 우대</span>
        <span class="tag">희귀도 확률 적용</span>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("🔍 생물 발견하기", use_container_width=True):
        result = discover_species(habitat)
        if result:
            found, is_new, message = result
            st.session_state.latest_message = message
            st.session_state.latest_is_new = is_new
            st.rerun()

    if st.session_state.last_found:
        found = SPECIES_BY_ID.get(st.session_state.last_found)
        if found:
            rarity = found["rarity"]
            rarity_info = RARITIES[rarity]
            st.markdown("---")
            st.markdown("## 🎉 발견 결과")

            if st.session_state.get("latest_is_new", False):
                st.success("✨ 새로운 생물을 발견했어요!")
            else:
                st.info("🔁 이미 발견한 생물을 다시 만났어요.")

            st.markdown(
                f"""<div class="panel">
                <h2>{rarity_info['emoji']} {found['name']}</h2>
                <span class="tag">{found['group']}</span>
                <span class="tag">{found['rarity']}</span>
                <span class="tag">{found['english']}</span>
                <p>{found['fact']}</p>
                <p class="small-note">이 생물의 발견 경험치: {rarity_info['xp']} XP</p>
                </div>""",
                unsafe_allow_html=True,
            )

            photo_col, info_col = st.columns([1, 2])
            with photo_col:
                display_photo(found, width=200)
            with info_col:
                st.markdown("### 🔬 생물 정보")
                st.write(f"**분류:** {found['group']}")
                st.write(f"**주요 서식지:** {', '.join(found['habitats'])}")
                st.write(f"**희귀도:** {found['rarity']}")
                st.write(f"**특징:** {found['fact']}")
                st.write(f"**도감 보유 수:** {st.session_state.collection.get(found['id'], 0)}")
                st.caption(st.session_state.get("latest_message", ""))

    st.markdown("---")
    st.markdown("### 🎲 희귀도 출현 확률")
    st.caption(
        "기본 가중치 기준 비율이에요. 실제 출현 확률은 서식지에 존재하는 생물의 종류와 "
        "미발견 생물 우대 효과에 따라 달라질 수 있어요."
    )
    rarity_cols = st.columns(5)
    for col, (name, data) in zip(rarity_cols, RARITIES.items()):
        with col:
            st.markdown(
                f"""<div class="panel" style="text-align:center;border-top:5px solid {data['color']};">
                <div style="font-size:1.5rem;">{data['emoji']}</div>
                <b>{name}</b><br>
                <span class="small-note">기본 가중치 {data['weight']}</span><br>
                <b>+{data['xp']} XP</b>
                </div>""",
                unsafe_allow_html=True,
            )

# =========================================================
# 12. 생물 도감
# =========================================================

elif page == "📖 생물 도감":
    st.markdown("## 📖 나의 생물 도감")
    st.write("발견한 생물은 상세 정보를 볼 수 있어요.")

    f1, f2 = st.columns(2)
    with f1:
        group_filter = st.selectbox("분류", ["전체"] + GROUPS)
    with f2:
        rarity_filter = st.selectbox("희귀도", ["전체"] + list(RARITIES.keys()))

    visible = []
    for s in SPECIES:
        if group_filter != "전체" and s["group"] != group_filter:
            continue
        if rarity_filter != "전체" and s["rarity"] != rarity_filter:
            continue
        visible.append(s)

    st.caption(f"표시 중인 생물 {len(visible)}종")

    for start in range(0, len(visible), 2):
        cols = st.columns(2)
        for col, species in zip(cols, visible[start:start + 2]):
            with col:
                count = st.session_state.collection.get(species["id"], 0)
                found = count > 0
                rarity = RARITIES[species["rarity"]]
                with st.container(border=True):
                    if found:
                        st.markdown(
                            f"### {rarity['emoji']} {species['name']}"
                        )
                        st.caption(
                            f"{species['english']} · {species['group']} · {species['rarity']}"
                        )
                        st.write(species["fact"])
                        st.caption(f"보유 수: {count}")
                        with st.expander("📷 사진과 상세 정보"):
                            display_photo(species, width=180)
                            st.write("**서식지:** " + ", ".join(species["habitats"]))
                    else:
                        st.markdown("### ❔ 미발견 생물")
                        st.caption(f"{species['group']} · {species['rarity']}")
                        st.write("아직 발견하지 못한 생물이에요.")
                        st.caption("해당 생물이 서식하는 지역을 탐험해 보세요!")

# =========================================================
# 13. 생명과학 퀴즈
# =========================================================

elif page == "🧪 생명과학 퀴즈":
    st.markdown("## 🧪 생명과학 연구소")
    st.write("생명과학 지식을 시험하고 경험치를 얻어 보세요.")

    difficulty_rewards = {"쉬움": 10, "보통": 25, "어려움": 50}
    difficulty = st.selectbox("퀴즈 난이도", list(QUIZZES.keys()))

    st.markdown(
        f"""<div class="panel">
        <h3>📚 {difficulty} 난이도</h3>
        <p>정답을 맞히면 <b>+{difficulty_rewards[difficulty]} XP</b>를 받아요.</p>
        <p class="small-note">문제는 생명과학의 기본 개념부터 유전자 재조합과 생태학까지 포함해요.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("🎯 새 문제 받기", use_container_width=True):
        st.session_state.quiz_question = random.choice(QUIZZES[difficulty])
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_answered = False
        st.session_state.quiz_result = None
        st.rerun()

    question = st.session_state.quiz_question
    if question:
        q, options, answer, explanation = question
        q_difficulty = st.session_state.get("quiz_difficulty", difficulty)
        st.markdown("---")
        st.markdown(f"### ❓ {q}")
        choice = st.radio(
            "정답을 선택하세요",
            options,
            index=None,
            key=f"answer_{q_difficulty}_{q}",
        )

        if not st.session_state.quiz_answered:
            if st.button("정답 확인", use_container_width=True):
                if choice is None:
                    st.warning("선택지를 먼저 골라 주세요.")
                else:
                    is_correct = options.index(choice) == answer
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_result = {
                        "correct": is_correct,
                        "explanation": explanation,
                        "answer": options[answer],
                        "difficulty": q_difficulty,
                    }

                    st.session_state.quiz_total += 1
                    if is_correct:
                        st.session_state.quiz_correct += 1
                        st.session_state.xp += difficulty_rewards[q_difficulty]
                    save_game()
                    st.rerun()

        if st.session_state.quiz_answered and st.session_state.quiz_result:
            result = st.session_state.quiz_result
            if result["correct"]:
                st.success(
                    f"정답이에요! +{difficulty_rewards[result['difficulty']]} XP"
                )
            else:
                st.error(f"아쉬워요. 정답은 '{result['answer']}'예요.")

            st.info(f"💡 해설: {result['explanation']}")
            st.caption(
                f"누적 정답: {st.session_state.quiz_correct} / "
                f"{st.session_state.quiz_total}"
            )

    else:
        st.info("새 문제 받기를 눌러 퀴즈를 시작하세요.")

# =========================================================
# 14. 업적
# =========================================================

elif page == "🏆 업적":
    st.markdown("## 🏆 탐험 업적")
    found_count = len(st.session_state.collection)
    habitats_found = set(
        item.get("habitat")
        for item in st.session_state.discovery_log
    )

    achievements = [
        ("🌱 첫 발견", st.session_state.found_total >= 1,
         "첫 생물을 발견하세요."),
        ("📚 수집가", found_count >= 5,
         "서로 다른 생물 5종을 발견하세요."),
        ("🔬 생물 연구가", found_count >= 20,
         "서로 다른 생물 20종을 발견하세요."),
        ("🌳 자연 전문가", found_count >= 50,
         "서로 다른 생물 50종을 발견하세요."),
        ("👑 전설의 탐험가", found_count >= 100,
         "도감 100종을 완성하세요."),
        ("🧠 퀴즈 입문", st.session_state.quiz_correct >= 5,
         "퀴즈 정답 5개를 맞히세요."),
        ("🧪 지식의 달인", st.session_state.quiz_correct >= 20,
         "퀴즈 정답 20개를 맞히세요."),
        ("✨ 레벨 5", level >= 5,
         "탐험 레벨 5에 도달하세요."),
    ]

    for title, unlocked, description in achievements:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### {title}")
                st.caption(description)
            with c2:
                if unlocked:
                    st.success("달성!")
                else:
                    st.info("진행 중")

    st.markdown("### 📜 최근 탐험 기록")
    if st.session_state.discovery_log:
        for item in reversed(st.session_state.discovery_log[-15:]):
            label = "신규 발견" if item.get("new") else "중복 발견"
            st.write(
                f"**{item.get('time', '')}** · "
                f"{item.get('habitat', '')} · "
                f"{item.get('name', '')} · "
                f"{item.get('rarity', '')} · {label}"
            )
    else:
        st.info("아직 탐험 기록이 없어요.")

# =========================================================
# 15. 설정과 기록 초기화
# =========================================================

elif page == "⚙️ 설정":
    st.markdown("## ⚙️ 탐험 설정")

    st.markdown("### 💾 저장 정보")
    st.write(f"현재 저장 코드: `{st.session_state.save_code}`")
    st.caption("저장 코드는 다른 사람에게 알려 주지 않는 것을 권장해요.")

    if st.button("☁️ 지금 기록 저장하기", use_container_width=True):
        if save_game():
            st.success("탐험 기록을 데이터베이스에 저장했어요.")
        else:
            st.error("저장에 실패했어요. Supabase 연결 설정을 확인해 주세요.")

    st.markdown("---")
    st.markdown("### 🧹 탐험 기록 초기화")
    st.warning(
        "초기화하면 이 저장 코드에 연결된 도감, 경험치, 퀴즈 기록이 모두 사라져요. "
        "삭제한 기록은 되돌릴 수 없어요."
    )

    confirm = st.checkbox("탐험 기록을 모두 초기화하는 것에 동의합니다.")
    confirm_code = st.text_input(
        "확인을 위해 현재 저장 코드를 입력하세요",
        type="password",
    )

    if st.button("🗑️ 모든 탐험 기록 초기화", use_container_width=True):
        if not confirm:
            st.error("초기화 동의 항목을 체크해 주세요.")
        elif confirm_code != st.session_state.save_code:
            st.error("저장 코드가 일치하지 않아요.")
        else:
            reset_progress()
            if save_game():
                st.success("탐험 기록을 초기화하고 저장했어요.")
                st.rerun()
            else:
                st.error("데이터베이스 저장에 실패했어요. 기록을 완전히 초기화하지 못했을 수 있어요.")

    st.markdown("---")
    st.markdown("### ℹ️ 앱 정보")
    st.write(f"등록된 생물: {len(SPECIES)}종")
    st.write(f"생물 분류: {len(GROUPS)}개")
    st.write(f"퀴즈: 총 {sum(len(v) for v in QUIZZES.values())}문제")
    st.write("희귀도: 일반 · 고급 · 희귀 · 초희귀 · 전설")
    st.caption(
        "사진은 Wikipedia에서 가져오므로 일부 생물은 사진이 없거나 "
        "영어 페이지와 다른 사진이 표시될 수 있어요."
    )

# =========================================================
# 16. 하단 정보
# =========================================================

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6c8474;font-size:.85rem;'>"
    "🌿 BIO HUNTER · 자연을 발견하고 생명과학을 배우는 탐험 게임"
    "</div>",
    unsafe_allow_html=True,
)
