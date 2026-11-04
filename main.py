            )
            rarity = st.selectbox(
                "희귀도 선택", ["전체"] + RARITY_ORDER, key=f"rar_{terrain}"
            )

            visible = [
                s for s in terrain_species
                if (category == "전체" or s["category"] == category)
                and (rarity == "전체" or s["rarity"] == rarity)
            ]
            st.caption(f"이 지형에서 확인할 수 있는 생물: {len(visible)}종")

            for start in range(0, len(visible), 3):
                cols = st.columns(3)
                for col, creature in zip(cols, visible[start:start + 3]):
                    with col:
                        name = creature["name"]
                        is_found = name in st.session_state.discovered
                        with st.container(border=True):
                            if is_found:
                                show_creature_image(creature, width=160)
                                st.markdown(f"### {creature['emoji']} {name}")
                                st.write(creature["description"])
                                st.caption(
                                    f"{RARITY_INFO[creature['rarity']]['emoji']} "
                                    f"{creature['rarity']} · {creature['category']}"
                                )
                                st.caption(
                                    f"발견 횟수: "
                                    f"{st.session_state.discovered[name]['count']}회"
                                )
                            else:
                                st.markdown(
                                    "<div style='font-size:65px;text-align:center'>❓</div>",
                                    unsafe_allow_html=True,
                                )
                                st.markdown("### 미발견 생물")
                                st.write("탐험에서 퀴즈를 맞혀 발견해 보자!")
                                st.caption(
                                    f"{RARITY_INFO[creature['rarity']]['emoji']} "
                                    f"{creature['rarity']} · {creature['category']}"
                                )

# =========================================================
# 10. 업적
# =========================================================

elif st.session_state.page == "🏆 업적":
    st.header("🏆 탐험 업적")
    found = len(st.session_state.discovered)

    milestones = [
        (1, "첫 발견", "처음으로 생물을 도감에 등록하기"),
        (5, "자연 탐험가", "5종의 생물 발견하기"),
        (10, "생물 수집가", "10종의 생물 발견하기"),
        (25, "생태계 전문가", "25종의 생물 발견하기"),
        (50, "바이오 마스터", "50종의 생물 발견하기"),
        (100, "전설의 탐험가", "100종의 생물 발견하기"),
        (200, "자연의 수호자", "200종의 생물 발견하기"),
        (300, "바이오 레전드", "300종의 생물 발견하기"),
    ]

    for target, title, description in milestones:
        if found >= target:
            st.success(f"🏅 **{title}** — {description}")
        else:
            st.write(f"🔒 **{title}** — {description} ({found}/{target})")

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
    b.metric("발견한 종류", found)
    c.metric("놓친 횟수", st.session_state.total_missed)

# =========================================================
# 11. 설정
# =========================================================

elif st.session_state.page == "⚙️ 설정":
    st.header("⚙️ 설정")
    st.write("현재 세션의 탐험 기록을 확인하고 초기화할 수 있어.")
    st.caption("수집 기록은 영구 저장되지 않아. 앱 세션이 초기화되면 기록도 사라져.")

    st.metric("도감 생물 종류", len(SPECIES))
    st.metric("발견한 종류", len(st.session_state.discovered))
    st.metric("획득 경험치", st.session_state.xp)
    st.metric("놓친 생물", st.session_state.total_missed)

    st.divider()
    st.subheader("기록 초기화")
    confirm = st.checkbox(
        "현재 세션의 도감과 경험치를 초기화하는 것에 동의해.",
        key="confirm_reset",
    )

    if st.button("🗑️ 게임 기록 초기화", disabled=not confirm):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.session_state.page = "⚙️ 설정"
        st.success("현재 게임 기록을 초기화했어.")
        st.rerun()

st.divider()
st.caption("🌱 생물 다양성 탐사 | 생물과 생태계를 발견하고 기록하는 탐사 프로젝트")
