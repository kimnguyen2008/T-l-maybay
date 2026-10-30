import os
import sys
import subprocess
import json
import asyncio
import time
import urllib.parse
import re
from datetime import datetime

def install_requirements():
    packages = ["requests", "websockets", "rich"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[*] Đang cài đặt thư viện thiếu: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_requirements()

import requests
import websockets
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich import box

HEADERS_MOBILE = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
}

console = Console()

def load_history():
    filename = "history_aero.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(history):
    filename = "history_aero.json"
    with open(filename, 'w') as f:
        json.dump(history[-100:], f)

def login_game(json_data):
    url = "https://aero.turbogg4u.online/api/common/profile"
    try:
        response = requests.post(url, headers=HEADERS_MOBILE, data=json_data.encode('utf-8'))
        data = response.json()
        if "token" in data and "id" in data:
            return {
                "success": True,
                "player_id": data["sub"],
                "wss_token": data["token"],
                "balance": data.get("balance", 0)
            }
        return {"success": False, "msg": "Không tìm thấy token trong phản hồi."}
    except Exception as e:
        return {"success": False, "msg": str(e)}

def tac_chien_tong_luc(history):
    if len(history) < 10:
        return True, 1.15

    recent_3 = history[-3:]
    recent_5 = history[-5:]
    recent_10 = history[-10:]

    so_van_chet_som = sum(1 for x in recent_10 if x < 1.5)
    so_van_chet_rat_som = sum(1 for x in recent_5 if x < 1.2)
    
    trend_up = recent_3[2] > recent_3[1] > recent_3[0]

    if so_van_chet_rat_som >= 3:
        return False, 0.0
        
    if history[-1] < 1.1 and history[-2] < 1.1:
        return False, 0.0
        
    if history[-1] >= 15.0:
        return False, 0.0

    if so_van_chet_som >= 7:
        return True, 1.05

    if all(1.2 <= x <= 1.9 for x in recent_5):
        return True, 3.15
        
    if trend_up and recent_3[-1] > 2.0:
        return True, 1.85

    if history[-1] < 1.5 and history[-2] >= 2.0:
        return True, 1.25

    return True, 1.15

# --- IN BANNER CHÀO MỪNG L-TOOL ---
def print_banner_ltool():
    console.clear()
    banner_text = Text(r"""
██╗          ████████╗ ██████╗  ██████╗ ██╗
██║          ╚══██╔══╝██╔═══██╗██╔═══██╗██║
██║    █████╗   ██║   ██║   ██║██║   ██║██║
██║    ╚════╝   ██║   ██║   ██║██║   ██║██║
███████╗        ██║   ╚██████╔╝╚██████╔╝███████╗
╚══════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
""", style="bold red")
    
    info_text = Text()
    info_text.append("👤 ADMIN: ", style="bold yellow")
    info_text.append("Lương Anh, Vĩ Luân, Nguyên, Khánh Huy,Huy G@y nha ae\n", style="bold white")
    info_text.append("📢 ZALO GROUP: ", style="bold yellow")
    info_text.append("https://zalo.me/g/ljtglc229\n", style="bold white")
    info_text.append("🛠️ PHIÊN BẢN: ", style="bold yellow")
    info_text.append("V1\n", style="bold white")

    panel = Panel(
        Align.center(Text.assemble(banner_text, "\n", info_text)),
        border_style="cyan",
        box=box.DOUBLE,
        title="[bold green]AERO BY L-TOOL[/bold green]",
        subtitle="[italic]CHÚC CÁC BẠN MAY MẮN[/italic]"
    )
    console.print(panel)

# --- BẢNG CHIA VỐN ---
def hien_thi_bang_chia_von_rich(tong_von, cuoc_co_ban, he_so_nhan, so_tay_toi_da):
    table = Table(title="[bold yellow]BẢNG LỘ TRÌNH VỐN CHI TIẾT[/bold yellow]", box=box.DOUBLE_EDGE)
    table.add_column("Tay", justify="center", style="cyan", no_wrap=True)
    table.add_column("Mức cược", justify="right", style="magenta")
    table.add_column("Tổng vốn đã vào", justify="right", style="blue")
    table.add_column("Vốn còn dư", justify="right", style="green")

    von_hien_tai = float(tong_von)
    cuoc_hien_tai = float(cuoc_co_ban)
    tong_da_cuoc = 0.0

    console.print("\n")
    for tay in range(1, int(so_tay_toi_da) + 1):
        if von_hien_tai < cuoc_hien_tai:
            console.print(f"[bold red]🚨 CẢNH BÁO: Gãy vốn ở tay thứ {tay}! Vốn còn dư ({von_hien_tai:,.2f}) KHÔNG ĐỦ để vào cược ({cuoc_hien_tai:,.2f}).[/bold red]")
            break

        tong_da_cuoc += cuoc_hien_tai
        von_hien_tai -= cuoc_hien_tai
        
        table.add_row(
            str(tay),
            f"{cuoc_hien_tai:,.2f}",
            f"{tong_da_cuoc:,.2f}",
            f"{von_hien_tai:,.2f}"
        )

        cuoc_hien_tai *= float(he_so_nhan)
        
    console.print(table)
    console.print("\n")

# --- GIAO DIỆN UI BẰNG RICH ---
def add_log(session, msg):
    time_str = datetime.now().strftime("%H:%M:%S")
    session['logs'].append(f"[{time_str}] {msg}")
    if len(session['logs']) > 8: 
        session['logs'].pop(0)

def generate_ui(session):
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=10)
    )
    layout["main"].split_row(
        Layout(name="game_view", ratio=2),
        Layout(name="history_view", ratio=1)
    )

    cur = session.get('currency', 'bld').upper()
    mode_str = "Tự động tính X" if session['auto_x'] else f"Cố định X {session['target_x']}"
    header_text = Text(f"💰 Số dư: {session['current_balance']:.2f} {cur} | 🎯 Cược: {session['current_bet']:.0f} {cur} | 🎲 Tổng ván: {session['total_played']} | ⚙️ Chế độ: {mode_str} | 📈 Lãi/Lỗ: {session['current_balance'] - session['initial_balance']:.2f} {cur}", style="bold yellow")
    layout["header"].update(Panel(Align.center(header_text, vertical="middle"), title="[bold cyan]L-TOOL AERO[/bold cyan]", border_style="cyan"))

    flying_x = session.get('last_flying_x', 0.0)
    if not session['is_betting'] and flying_x == 0.0:
        display_x = "[bold white]ĐANG CHỜ MÁY BAY CẤT CÁNH...[/bold white]"
    else:
        color = "green" if flying_x >= 2.0 else ("red" if flying_x < 1.5 else "yellow")
        display_x = f"[{color}]✈️ X {flying_x:.2f}[/{color}]"

    target_info = f"\n\n[cyan]Mục tiêu nhảy dù: X {session['target_x']}[/cyan]" if session.get('target_x') else ""
    status_info = f"\n[magenta]Trạng thái: {'Đang Cược 🎯' if session['bet_placed'] else 'Quan sát 👀'}[/magenta]"
    
    game_content = Align.center(Text.from_markup(f"\n\n{display_x}{target_info}{status_info}", justify="center"), vertical="middle")
    layout["game_view"].update(Panel(game_content, title="[bold green]KHUNG CHƠI[/bold green]", border_style="green"))

    history_table = Table(show_header=False, box=None)
    for h in reversed(session['history_x'][-12:]):
        color = "green" if h >= 2.0 else ("red" if h < 1.5 else "yellow")
        history_table.add_row(f"[{color}]• X {h:.2f}[/{color}]")
    layout["history_view"].update(Panel(Align.center(history_table), title="[bold blue]LỊCH SỬ BAY", border_style="blue"))

    log_text = "\n".join(session['logs'])
    layout["footer"].update(Panel(Text.from_markup(log_text), title="[bold white]NHẬT KÝ HỆ THỐNG", border_style="white"))

    return layout

# --- KẾT NỐI WEBSOCKET GAME ---
async def listen_game_server(session):
    ws_url = "wss://aero.turbogg4u.online/ws/gameserver"
    # Tối ưu mạng di động: nới lỏng ping interval để chống rớt mạng do lag nhẹ
    async with websockets.connect(ws_url, ping_interval=25, ping_timeout=20) as ws_game:
        while session['is_running']:
            msg = await ws_game.recv()
            if msg.startswith("1,"):
                sec = msg.split(",")[1]
                if sec in ["3", "2"] and not session['is_betting']:
                    session['is_betting'] = True
                    
                    if session['last_flying_x'] > 0:
                        session['history_x'].append(session['last_flying_x'])
                        save_history(session['history_x'])
                        
                        if session['observe_count'] < session['observe_target']:
                            session['observe_count'] += 1
                            add_log(session, f"🕵️‍♂️ BÁO CÁO THEO DÕI ({session['observe_count']}/{session['observe_target']}): Máy bay rơi tại X {session['last_flying_x']}")
                            
                            if session['observe_count'] == session['observe_target']:
                                add_log(session, "[bold green]🔥 HOÀN THÀNH THEO DÕI! Bắt đầu cược nào![/bold green]")
                        
                        elif session.get('pending_summary'):
                            s = session['pending_summary']
                            add_log(session, f"📊 KẾT QUẢ: {s['text_res']} | Chuỗi Thắng: {s['current_win_streak']} | Lãi Tổng: {s['total_profit']:.2f} {session['currency'].upper()}")
                            session['pending_summary'] = None
                            
                        session['last_flying_x'] = 0.0

                    if session['observe_count'] < session['observe_target']:
                        continue 

                    bet_amount = int(session['current_bet'])
                    
                    if session['current_balance'] < bet_amount:
                        session['is_running'] = False
                        session['stop_completely'] = True
                        add_log(session, f"🚨 [bold red]TẮT BOT! VÍ KHÔNG ĐỦ ({session['current_balance']} {session['currency'].upper()}).[/bold red]")
                        break 

                    if session['skip_count'] > 0:
                        session['skip_count'] -= 1
                        session['total_skipped'] += 1
                        add_log(session, f"[*] Đang theo dõi game... (Còn {session['skip_count']} ván nghỉ)")
                    
                    else:
                        should_bet = True
                        if session['auto_x']:                                    
                            should_bet, target_x = tac_chien_tong_luc(session['history_x'])
                            if should_bet:
                                session['target_x'] = target_x
                                add_log(session, f"🤖 L-TOOL: Chế độ Auto! Nhảy dù tại X {session['target_x']}")
                            else:
                                session['total_skipped'] += 1
                                add_log(session, "🛑 BÁO ĐỘNG: Bot sẽ bỏ qua ván này cho an toàn!")
                        
                        if should_bet:
                            bet_payload = {
                                "type": "placebet", "l": 1, "amount": bet_amount, "coefficient": "1000000",
                                "currency": session['currency'], "index": 0, "metadata": {"subPartnerId": "", "device": "mobile", "manual": True},
                                "theme": "default", "tag": "a"
                            }
                            await session['auth_send_queue'].put(json.dumps(bet_payload))

            elif msg.startswith("4,"):
                session['is_betting'] = False
                try:
                    current_x = float(msg.split(",")[1])
                    session['last_flying_x'] = current_x
                    
                    if session['bet_placed'] and not session['cashed_out'] and session['bet_id']:
                        trigger_point = session['target_x'] - 0.01
                        if trigger_point <= 1.0:
                            trigger_point = 1.01 
                            
                        if current_x >= trigger_point:
                            session['cashed_out'] = True
                            cashout_payload = {
                                "type": "cashout", "id": session['bet_id'], "amount": int(session['current_bet']),
                                "coefficient": current_x, 
                                "cashoutTimestamp": int(time.time() * 1000)
                            }
                            await session['auth_send_queue'].put(json.dumps(cashout_payload))
                            add_log(session, f"⚡ ĐÃ NHẢY DÙ! Kích hoạt chốt tại X {current_x:.2f}")
                        
                except ValueError:
                    pass
            
            if session.get('live_display'):
                session['live_display'].update(generate_ui(session))

# --- KẾT NỐI WEBSOCKET AUTH ---
async def listen_auth_server(session):
    safe_player_id = urllib.parse.quote(session['player_id'].replace("@", ":"))
    ws_url = f"wss://aero.turbogg4u.online/ws/v2/game/?playerId={safe_player_id}&token={session['wss_token']}"
    
    # Tối ưu mạng di động
    async with websockets.connect(ws_url, ping_interval=25, ping_timeout=20) as ws_auth:
        async def sender():
            while session['is_running']:
                data_to_send = await session['auth_send_queue'].get()
                await ws_auth.send(data_to_send)
                
        sender_task = asyncio.create_task(sender())
        
        try:
            while session['is_running']:
                msg = await ws_auth.recv()
                
                if "balance_ticket" in msg:
                    match = re.search(r'\[([\d\.]+),', msg)
                    if match:
                        session['current_balance'] = float(match.group(1))

                if msg.startswith("{"):
                    try:
                        data = json.loads(msg)
                        
                        if data.get("type") == "placed" and "data" in data:
                            session['bet_id'] = data["data"].get("id")
                            session['bet_placed'] = True
                            add_log(session, f"🎯 Đã lên máy bay với {int(session['current_bet'])} {session['currency'].upper()}! ID: {session['bet_id'][-8:]}")
                            
                        if data.get("type") == "result":
                            if session['bet_placed']:
                                session['total_played'] += 1
                                res = data.get("result")
                                payout = data.get("payout", 0)
                                amount = data.get("amount", session['current_bet'])
                                
                                if res == "won":
                                    profit_round = payout - amount
                                    session['current_win_streak'] += 1
                                    session['current_loss_streak'] = 0
                                    session['max_win_streak'] = max(session['max_win_streak'], session['current_win_streak'])
                                    session['current_bet'] = session['base_bet'] 
                                    text_res = f"[bold green]✅ HẠ CÁNH AN TOÀN (+{profit_round} {session['currency'].upper()})[/bold green]"
                                else:
                                    profit_round = -amount
                                    session['current_loss_streak'] += 1
                                    session['current_win_streak'] = 0
                                    session['max_loss_streak'] = max(session['max_loss_streak'], session['current_loss_streak'])
                                    session['current_bet'] *= session['loss_multiplier']
                                    session['skip_count'] = session['skip_after_loss']
                                    text_res = f"[bold red]❌ RỚT MÁY BAY ({profit_round} {session['currency'].upper()})[/bold red]"
                                
                                session['current_balance'] += profit_round
                                total_profit = session['current_balance'] - session['initial_balance']
                                
                                session['pending_summary'] = {
                                    "text_res": text_res,
                                    "target_x": session['target_x'],
                                    "total_played": session['total_played'],
                                    "total_profit": total_profit,
                                    "current_win_streak": session['current_win_streak']
                                }
                            
                            session['bet_id'] = None
                            session['bet_placed'] = False
                            session['cashed_out'] = False

                    except json.JSONDecodeError:
                        pass
        finally:
            sender_task.cancel()

# --- VÒNG LẶP CHẠY & AUTO RECONNECT ---
async def run_aero_bot(session):
    session['stop_completely'] = False
    
    while not session.get('stop_completely', False):
        if not session.get('logs'):
            add_log(session, "🟢 Đang kết nối máy chủ WebSocket...")
        session['is_running'] = True
        
        try:
            with Live(generate_ui(session), refresh_per_second=10) as live:
                session['live_display'] = live
                await asyncio.gather(
                    listen_game_server(session),
                    listen_auth_server(session)
                )
        except Exception as e:
            session['is_running'] = False
            error_name = type(e).__name__
            add_log(session, f"⚠️ MẤT KẾT NỐI ({error_name}). Đang khôi phục sau 3 giây...")
            await asyncio.sleep(3) 
            
    print("\n🛑 HỆ THỐNG ĐÃ DỪNG HOẠT ĐỘNG HOÀN TOÀN.")

async def main():
    print_banner_ltool()
    
    while True:
        json_data = input("\n[Bước 1] Dán đoạn mã JSON tài khoản của bạn vào đây:\n> ").strip()
        if "token" in json_data:
            break
        print("❌ Dữ liệu không hợp lệ, vui lòng nhập lại JSON có chứa token.")

    console.print("\n⏳ Đang xác thực tài khoản qua API...", style="yellow")
    result = login_game(json_data)
    
    if not result["success"]:
        console.print(f"❌ Khước từ quyền truy cập: {result['msg']}", style="red")
        return

    loaded_history = load_history()
    console.print(f"✅ Xác thực thành công! Số dư hiện tại: {result['balance']}", style="green")
    console.print(f"📂 Đã khôi phục {len(loaded_history)} bộ hồ sơ tình báo lịch sử.", style="blue")

    currency_map = {"1": "bld", "2": "usdt", "3": "xworld"}
    currency_code = "bld"
    while True:
        print("\n[Cấu hình Tiền tệ] Chọn loại tiền tệ bạn muốn cược:")
        print("1. BLD (Mặc định)")
        print("2. USDT")
        print("3. XWORLD")
        c_choice = input("Nhập lựa chọn (1-3): ").strip()
        if c_choice in currency_map:
            currency_code = currency_map[c_choice]
            break
        elif c_choice == "":
            break
        print("❌ Lựa chọn không hợp lệ.")

    session = {
        "player_id": result["player_id"],
        "wss_token": result["wss_token"],
        "is_running": False,
        "bet_id": None,
        "bet_placed": False,
        "cashed_out": False,
        "currency": currency_code,
        "is_betting": False,
        "auth_send_queue": asyncio.Queue(),
        "initial_balance": result['balance'],
        "current_balance": result['balance'],
        "total_played": 0,
        "total_skipped": 0,
        "current_win_streak": 0,
        "current_loss_streak": 0,
        "max_win_streak": 0,
        "max_loss_streak": 0,
        "history_x": loaded_history,
        "last_flying_x": 0.0,
        "pending_summary": None,
        "skip_count": 0,
        "logs": [], 
        "live_display": None,
        "target_x": 1.2 
    }

    # --- BƯỚC 2: MENU QUẢN LÝ VỐN ---
    while True:
        print(f"\n[Bước 2] THIẾT LẬP QUẢN LÝ VỐN (Số dư hiện tại: {session['current_balance']} {session['currency'].upper()}):")
        print("1. Nhập thủ công (Tự nhập cược gốc & hệ số nhân)")
        print("2. Tự động chia vốn (Nhập số tay muốn nuôi & hệ số nhân -> Máy tự tính cược gốc)")
        chon_von = input(">> Chọn 1 hoặc 2: ").strip()

        if chon_von == '1':
            while True:
                try:
                    bet_amount = int(input("   -> Nhập số tiền cược gốc mỗi ván (Tối thiểu 10): "))
                    if bet_amount >= 10:
                        session['base_bet'] = bet_amount
                        session['current_bet'] = bet_amount
                        break
                    print("   ❌ Tiền cược không được nhỏ hơn 10.")
                except ValueError:
                    print("   ❌ Yêu cầu nhập số nguyên.")
            
            while True:
                try:
                    loss_multi = float(input("   -> Nhập hệ số nhân tiền cược sau khi THUA (VD: 2.0): "))
                    if loss_multi >= 1.0:
                        session['loss_multiplier'] = loss_multi
                        break
                    print("   ❌ Vui lòng nhập hệ số hợp lệ (>= 1.0).")
                except ValueError:
                    print("   ❌ Yêu cầu nhập số.")
            
            xem_bang = input("\n   [?] Bạn có muốn xem thử bảng dự phòng gãy vốn không? (y/n): ").strip().lower()
            if xem_bang == 'y':
                try:
                    so_tay_test = int(input("   >> Nhập số tay muốn test lộ trình: "))
                    hien_thi_bang_chia_von_rich(session['current_balance'], session['base_bet'], session['loss_multiplier'], so_tay_test)
                except ValueError: pass
            break

        elif chon_von == '2':
            while True:
                try:
                    so_tay = int(input("   -> Bạn muốn chia vốn để gồng tối đa bao nhiêu tay? (VD: 5): "))
                    if so_tay > 0:
                        break
                    print("   ❌ Số tay phải lớn hơn 0.")
                except ValueError:
                    print("   ❌ Yêu cầu nhập số nguyên.")
            
            while True:
                try:
                    loss_multi = float(input("   -> Nhập hệ số nhân tiền cược sau khi THUA (VD: 2.0): "))
                    if loss_multi >= 1.0:
                        session['loss_multiplier'] = loss_multi
                        break
                    print("   ❌ Vui lòng nhập hệ số hợp lệ (>= 1.0).")
                except ValueError:
                    print("   ❌ Yêu cầu nhập số.")

            he_so_tong = 0
            for i in range(so_tay):
                he_so_tong += (session['loss_multiplier'] ** i)
            
            calc_base = int(session['current_balance'] / he_so_tong)
            
            if calc_base < 10:
                print(f"\n   ❌ CẢNH BÁO: Vốn của bạn ({session['current_balance']}) KHÔNG ĐỦ để nuôi {so_tay} tay với hệ số nhân {session['loss_multiplier']}.")
                print(f"   Tính toán ra cược gốc chỉ được {calc_base} (nhỏ hơn mức tối thiểu sàn cho phép là 10).")
                print("   Vui lòng thiết lập lại số tay hoặc hệ số nhân thấp hơn!\n")
                continue 
            else:
                session['base_bet'] = calc_base
                session['current_bet'] = calc_base
                print(f"\n   ✅ Đã tự động chia vốn thành công! Cược gốc an toàn của bạn là: {calc_base}")
                hien_thi_bang_chia_von_rich(session['current_balance'], session['base_bet'], session['loss_multiplier'], so_tay)
                break
        
        else:
            print("❌ Lựa chọn không hợp lệ. Vui lòng gõ 1 hoặc 2.")

    while True:
        target_input = input("\n[Bước 3] Chốt lãi ở X? (Gõ số ví dụ: 1.5, hoặc gõ 'auto' để bật BOT tự tính): ").strip().lower()
        if target_input == 'auto':
            session['auto_x'] = True
            break
        else:
            try:
                session['target_x'] = float(target_input)
                session['auto_x'] = False
                break
            except ValueError:
                print("❌ Tọa độ không hợp lệ. Vui lòng nhập số hoặc 'auto'.")

    while True:
        try:
            session['skip_after_loss'] = int(input("\n[Bước 4] Tạm nghỉ mấy ván sau khi THUA? (Ví dụ: 0, 1, 2...): "))
            if session['skip_after_loss'] >= 0:
                break
        except ValueError:
            print("❌ Vui lòng nhập số nguyên.")

    while True:
        try:
            session['observe_target'] = int(input("\n[Bước 5] Theo dõi bao nhiêu ván trước khi bắt đầu đánh? (Gõ 0 để đánh ngay): "))
            if session['observe_target'] >= 0:
                session['observe_count'] = 0
                break
        except ValueError:
            print("❌ Vui lòng nhập số nguyên (>= 0).")

    input("\nNhấn phím [ENTER] để chính thức BẮT ĐẦU CƯỢC và mở giao diện...")
    
    os.system('cls' if os.name == 'nt' else 'clear')
    await run_aero_bot(session)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n🛑 [bold red]ĐÃ DỪNG TOOL BẰNG LỆNH.[/bold red]")
        sys.exit(0)
