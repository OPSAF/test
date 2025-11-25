import streamlit as st
import random
import time

# 侧边栏 - 难度
st.sidebar.title("游戏设置")

difficulty = st.sidebar.radio("难度级别", ["简单", "中等", "困难"])

def initialize_game():
    """初始化游戏状态"""
    if 'game_state' not in st.session_state:
        # 创建卡片对（使用表情符号和数字组合）
        symbols = ['🛐', '⚛️', '✡️', '☸️', '☯️', '✝️', '☦️', '☪️', 
                  '🕎', '🔯', '🪯', '☮️', '🕉️']
        # 根据难度调整噪声
        level = {"简单": 4, "中等": 8, "困难": 13}[difficulty]
        
        cards = symbols[:level] * 2  #
        random.shuffle(cards)
        
        st.session_state.game_state = {
            'cards': cards,
            'flipped': [False] * 16,
            'matched': [False] * 16,
            'first_card': None,
            'second_card': None,
            'moves': 0,
            'matches': 0,
            'game_started': False,
            'start_time': None,
            'game_over': False
        }


def flip_card(card_index):
    """翻转卡片"""
    state = st.session_state.game_state
    
    if (state['flipped'][card_index] or state['matched'][card_index] or 
        state['second_card'] is not None):
        return
    
    if not state['game_started']:
        state['game_started'] = True
        state['start_time'] = time.time()
    
    if state['first_card'] is None:
        state['first_card'] = card_index
        state['flipped'][card_index] = True
    else:
        state['second_card'] = card_index
        state['flipped'][card_index] = True
        state['moves'] += 1
        
        # 检查是否匹配
        if state['cards'][state['first_card']] == state['cards'][state['second_card']]:
            state['matched'][state['first_card']] = True
            state['matched'][state['second_card']] = True
            state['matches'] += 1
            state['first_card'] = None
            state['second_card'] = None
            
            # 检查游戏是否结束
            if state['matches'] == 8:
                state['game_over'] = True
                state['end_time'] = time.time()
        else:
            # 不匹配，稍后翻回
            st.session_state.wait_for_flip = True

def reset_cards():
    """重置不匹配的卡片"""
    if st.session_state.wait_for_flip:
        state = st.session_state.game_state
        state['flipped'][state['first_card']] = False
        state['flipped'][state['second_card']] = False
        state['first_card'] = None
        state['second_card'] = None
        st.session_state.wait_for_flip = False

def display_card(card_index, symbol):
    """显示单个卡片"""
    state = st.session_state.game_state
    flipped = state['flipped'][card_index]
    matched = state['matched'][card_index]
    
    # 卡片样式
    if matched:
        button_style = """
        <style>
            .matched-card {
                background-color: #4CAF50 !important;
                color: white !important;
                border: 2px solid #45a049 !important;
            }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        st.button(symbol, key=f"card_{card_index}", 
                 use_container_width=True, disabled=True,
                 help="已匹配")
    elif flipped:
        st.button(symbol, key=f"card_{card_index}", 
                 use_container_width=True, disabled=True,
                 help="已翻开")
    else:
        if st.button("?", key=f"card_{card_index}", 
                    use_container_width=True,
                    help="点击翻开"):
            flip_card(card_index)
            st.rerun()

def main():
    st.set_page_config(
        page_title="翻牌测试游戏",
        page_icon="🎮",
        layout="wide"
    )
    
    # 自定义CSS样式
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .game-instructions {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🧠 记忆翻牌游戏</div>', 
                unsafe_allow_html=True)
    
    # 初始化游戏
    initialize_game()
    
    # 游戏说明
    with st.expander("📋 游戏说明", expanded=True):
        st.markdown("""
        游戏规则：
        - 找到所有匹配的卡片对
        - 每次翻开两张卡片
        - 如果匹配，卡片保持翻开状态
        - 如果不匹配，卡片会自动翻回
        - 用最少的步数完成所有匹配！
        
        """)
    
    state = st.session_state.game_state
    
    # 游戏统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("步数", state['moves'])
    
    with col2:
        st.metric("已匹配", f"{state['matches']}/8")
    
    with col3:
        if state['game_started'] and not state['game_over']:
            elapsed_time = int(time.time() - state['start_time'])
            st.metric("用时", f"{elapsed_time}秒")
        else:
            st.metric("用时", "0秒")
    
    with col4:
        if state['moves'] > 0:
            efficiency = round(state['matches'] / state['moves'] * 100, 1) if state['moves'] > 0 else 0
            st.metric("匹配效率", f"{efficiency}%")
        else:
            st.metric("匹配效率", "0%")
    
    # 游戏网格布局
    st.markdown("---")
    st.subheader("游戏区域")
    
    # 4x4网格
    cols = st.columns(4)
    for i in range(16):
        with cols[i % 4]:
            if state['flipped'][i] or state['matched'][i]:
                display_card(i, state['cards'][i])
            else:
                display_card(i, "?")
    
    # 游戏控制按钮
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        if st.button("🔄 重新开始游戏", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'wait_for_flip':
                    del st.session_state[key]
            st.rerun()
    
    # 处理卡片翻转延迟
    if st.session_state.get('wait_for_flip', False):
        time.sleep(0.5)  # 显示0.5秒后翻回
        reset_cards()
        st.rerun()
    
    # 游戏结束显示
    if state['game_over']:
        st.balloons()
        total_time = int(state['end_time'] - state['start_time'])
        
        st.success(f"""
        🎉 恭喜！你完成了游戏！
        
        **成绩统计：**
        - 总步数: {state['moves']} 步
        - 总用时: {total_time} 秒
        - 匹配效率: {round(8/state['moves']*100, 1)}%
        
        {'🌟 完美表现！' if state['moves'] == 8 else '👍 很棒的表现！' if state['moves'] <= 16 else '💪 继续努力！'}
        """)
        
        # 性能评估
        if state['moves'] == 8:
            st.markdown("**🏆 记忆大师！你找到了最优解！**")
        elif state['moves'] <= 16:
            st.markdown("**🥈 优秀表现！你的记忆力很棒！**")
        elif state['moves'] <= 24:
            st.markdown("**🥉 良好表现！继续锻炼记忆力！**")
        else:
            st.markdown("**📚 多加练习，记忆力会越来越好！**")

if __name__ == "__main__":
    main()
