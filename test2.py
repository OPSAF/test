import streamlit as st
import random
import time

def initialize_game(difficulty):
    """初始化游戏状态"""
    # 创建卡片对（使用表情符号）
    symbols = ['🛐', '⚛️', '✡️', '☸️', '☯️', '✝️', '☦️', '☪️', 
              '🕎', '🔯', '🪯', '☮️', '🕉️']
    
    # 根据难度调整卡片数量
    difficulty_settings = {
        "简单": 4,  # 4对卡片，8张
        "中等": 6,  # 6对卡片，12张
        "困难": 8   # 8对卡片，16张
    }
    
    num_pairs = difficulty_settings[difficulty]
    total_cards = num_pairs * 2
    
    # 随机选择符号
    selected_symbols = symbols[:num_pairs]
    cards = selected_symbols * 2
    random.shuffle(cards)
    
    st.session_state.game_state = {
        'cards': cards,
        'flipped': [False] * total_cards,
        'matched': [False] * total_cards,
        'first_card': None,
        'second_card': None,
        'moves': 0,
        'matches': 0,
        'game_started': False,
        'start_time': None,
        'game_over': False,
        'total_pairs': num_pairs,
        'difficulty': difficulty
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
            if state['matches'] == state['total_pairs']:
                state['game_over'] = True
                state['end_time'] = time.time()
        else:
            # 不匹配，稍后翻回
            st.session_state.wait_for_flip = True
            st.session_state.flip_time = time.time()

def reset_cards():
    """重置不匹配的卡片"""
    if st.session_state.get('wait_for_flip', False):
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

def get_grid_columns(total_cards):
    """根据卡片数量返回合适的列数"""
    if total_cards <= 8:
        return 4  # 2x4 网格
    elif total_cards <= 12:
        return 4  # 3x4 网格
    else:
        return 4  # 4x4 网格

def main():
    st.set_page_config(
        page_title="记忆翻牌游戏",
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
    .difficulty-easy {
        color: #28a745;
        font-weight: bold;
    }
    .difficulty-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .difficulty-hard {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">🧠 记忆翻牌游戏</div>', 
                unsafe_allow_html=True)
    
    # 侧边栏 - 难度设置
    st.sidebar.title("🎯 游戏设置")
    
    difficulty = st.sidebar.radio("难度级别", ["简单", "中等", "困难"])
    
    # 显示难度说明
    difficulty_info = {
        "简单": "4对卡片，适合初学者",
        "中等": "6对卡片，中等挑战",
        "困难": "8对卡片，记忆力大考验"
    }
    
    difficulty_class = {
        "简单": "difficulty-easy",
        "中等": "difficulty-medium", 
        "困难": "difficulty-hard"
    }
    
    st.sidebar.markdown(f'<p class="{difficulty_class[difficulty]}">{difficulty_info[difficulty]}</p>', 
                       unsafe_allow_html=True)
    
    # 初始化游戏
    if ('game_state' not in st.session_state or 
        st.session_state.game_state.get('difficulty') != difficulty):
        initialize_game(difficulty)
    
    state = st.session_state.game_state
    
    # 游戏说明
    with st.expander("📋 游戏说明", expanded=True):
        st.markdown(f"""
        游戏规则：
        - 找到所有匹配的卡片对（当前难度：{difficulty}）
        - 每次翻开两张卡片
        - 如果匹配，卡片保持翻开状态
        - 如果不匹配，卡片会自动翻回
        - 用最少的步数完成所有匹配！
        

        """)
    
    # 游戏统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("步数", state['moves'])
    
    with col2:
        st.metric("已匹配", f"{state['matches']}/{state['total_pairs']}")
    
    with col3:
        if state['game_started'] and not state['game_over']:
            elapsed_time = int(time.time() - state['start_time'])
            st.metric("用时", f"{elapsed_time}秒")
        else:
            st.metric("用时", "0秒")
    
    with col4:
        if state['moves'] > 0:
            efficiency = round(state['matches'] / state['moves'] * 100, 1)
            st.metric("匹配效率", f"{efficiency}%")
        else:
            st.metric("匹配效率", "0%")
    
    # 游戏网格布局
    st.markdown("---")
    st.subheader("🎲 游戏区域")
    
    total_cards = len(state['cards'])
    cols_per_row = get_grid_columns(total_cards)
    cols = st.columns(cols_per_row)
    
    for i in range(total_cards):
        with cols[i % cols_per_row]:
            if state['flipped'][i] or state['matched'][i]:
                display_card(i, state['cards'][i])
            else:
                display_card(i, "?")
    
    # 填充空白位置以保持布局整齐
    remaining_spots = cols_per_row - (total_cards % cols_per_row)
    if remaining_spots < cols_per_row:  # 如果不是整行
        for i in range(remaining_spots):
            with cols[(total_cards + i) % cols_per_row]:
                st.empty()
    
    # 游戏控制按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 重新开始游戏", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # 处理卡片翻转延迟
    if st.session_state.get('wait_for_flip', False):
        current_time = time.time()
        if current_time - st.session_state.flip_time >= 0.7:  # 0.7秒后翻回
            reset_cards()
            st.rerun()
        else:
            # 设置自动重新运行以检查时间
            time.sleep(0.1)
            st.rerun()
    
    # 游戏结束显示
    if state['game_over']:
        st.balloons()
        total_time = int(state['end_time'] - state['start_time'])
        total_pairs = state['total_pairs']
        
        # 性能评估
        perfect_moves = total_pairs  # 最优步数
        good_moves = total_pairs * 2  # 良好步数
        okay_moves = total_pairs * 3  # 合格步数
        
        if state['moves'] == perfect_moves:
            rating = "🌟 完美表现！记忆大师！"
            evaluation = "🏆 记忆大师！你找到了最优解！"
        elif state['moves'] <= good_moves:
            rating = "👍 很棒的表现！"
            evaluation = "🥈 优秀表现！你的记忆力很棒！"
        elif state['moves'] <= okay_moves:
            rating = "💪 良好表现！"
            evaluation = "🥉 良好表现！继续锻炼记忆力！"
        else:
            rating = "📚 多加练习！"
            evaluation = "📚 多加练习，记忆力会越来越好！"
        
        st.success(f"""
        🎉 恭喜！你完成了{difficulty}难度的游戏！
        
        **成绩统计：**
        - 总步数: {state['moves']} 步
        - 总用时: {total_time} 秒
        - 匹配效率: {round(total_pairs/state['moves']*100, 1) if state['moves'] > 0 else 0}%
        - 表现评价: {rating}
        """)
        
        st.markdown(f"**{evaluation}**")

if __name__ == "__main__":
    main()
