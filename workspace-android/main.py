"""
未注册光猫查询工具 - Kivy 安卓版
依赖: kivy, requests
打包: buildozer -v android debug
"""

import requests
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.cardview import CardView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.clock import Clock

# ============================================================
#  API 配置（与原脚本一致）
# ============================================================
API_URL = "http://183.215.60.137:9082/nms/common/invokeRemoteController/invoke.do"
HEADERS = {
    'Host': "183.215.60.137:9082",
    'User-Agent': "Mozilla/5.0 (Linux; Android 15; PKG110 Build/UKQ1.231108.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36",
    'Accept-Encoding': "gzip, deflate",
    'X-Requested-With': "XMLHttpRequest",
    'Origin': "http://183.215.60.137:9082",
    'Referer': "http://183.215.60.137:9082/nms/soc/sqm/toolkitMan/oltToolQuery.jsp",
    'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}


# ============================================================
#  API 函数
# ============================================================

def query_olt_by_name(dev_name):
    payload = {
        'serviceName': "broadbandManService",
        'methodName': "qryOltInformationByEqu",
        'param': json.dumps({"devName": dev_name}),
        'needTrans': "N"
    }
    headers = {**HEADERS, 'Cookie': "JSESSIONID=DE2E2DCE8CEC44D7691E734C0DE6258F"}
    try:
        resp = requests.post(API_URL, data=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            if data.get('resultData'):
                return True, data['resultData']
            return False, "未找到匹配的 OLT 设备"
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)


def get_onu_list(olt_ip, ems_name):
    payload = {
        'serviceName': "ablityPlatformInf",
        'methodName': "qryOltUnregisteredInfo",
        'param': json.dumps({
            "ZL_OLT_IP": olt_ip, "ZL_EMS_NAME": ems_name,
            "loginParam": "Cc1Bb3AaEeHh24Kk9Ee1Qq5Yy4Uu8Dd4Xx90asdQwer"
        }),
        'needTrans': "N"
    }
    headers = {**HEADERS, 'Cookie': "JSESSIONID=BD4C0975D36E0617307261E78C665E2E"}
    try:
        resp = requests.post(API_URL, data=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            if data.get('resultData'):
                return data['resultData'][0]['data'][0]['row']
    except Exception:
        pass
    return []


def get_olt_detail(olt_ip, ems_name):
    payload = {
        'serviceName': "ablityPlatformInf",
        'methodName': "qryOltInfo",
        'param': json.dumps({"ZL_OLT_IP": olt_ip, "ZL_EMS_NAME": ems_name}),
        'needTrans': "N"
    }
    headers = {**HEADERS, 'Cookie': "JSESSIONID=BD4C0975D36E0617307261E78C665E2E"}
    try:
        resp = requests.post(API_URL, data=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            if data.get('resultData'):
                return data['resultData'][0]['data'][0]['row'][0]
    except Exception:
        pass
    return None


def sn_match(onu_sn, keyword):
    """匹配：留空=全部通过；否则取后4位精确比较（自动剥离非字母数字字符）"""
    if not keyword:
        return True
    k = ''.join(c for c in keyword.strip() if c.isalnum())[-4:].upper()
    sn = onu_sn.strip().upper()
    if len(k) < 4:
        return False
    return k == sn[-4:]


# ============================================================
#  Kivy UI
# ============================================================

class Color:
    """配色常量"""
    PRIMARY     = (0.08, 0.45, 0.90, 1)   # 蓝
    SUCCESS     = (0.13, 0.75, 0.35, 1)   # 绿
    WARNING     = (0.95, 0.65, 0.10, 1)   # 黄/橙
    DANGER      = (0.90, 0.20, 0.20, 1)  # 红
    INFO        = (0.60, 0.40, 0.80, 1)  # 紫
    BG          = (0.94, 0.95, 0.97, 1)  # 背景灰
    CARD_BG     = (1, 1, 1, 1)
    TEXT_DARK   = (0.15, 0.15, 0.15, 1)
    TEXT_LIGHT  = (1, 1, 1, 1)
    TEXT_MUTED  = (0.50, 0.50, 0.55, 1)
    BORDER      = (0.82, 0.84, 0.88, 1)


class OltResultCard(CardView):
    """单个 OLT 的结果卡片"""
    def __init__(self, olt_ip, ems_name, olt_detail, all_onu, matched, sn_keyword, **kw):
        self.has_match = bool(matched)
        self.hit_color = (0.88, 0.98, 0.90, 1)
        self.norm_color = (0.97, 0.97, 0.97, 1)
        super().__init__(
            padding=dp(10), radius=[dp(12)], elevation=3,
            background_color=self.hit_color if matched else (1, 1, 1, 1),
            **kw
        )

        col = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        col.bind(minimum_height=col.setter('height'))

        # --- 卡片顶部：OLT 信息 ---
        total = len(all_onu)
        m_cnt = len(matched)
        keyword_suffix = sn_keyword.strip()[-4:].upper() if sn_keyword else ""
        hit_color = (0.13, 0.75, 0.35, 1) if matched else (0.50, 0.50, 0.55, 1)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36))
        lbl_ip = Label(
            text=f"[b]{olt_ip}[/b]  {ems_name}",
            markup=True, font_size=dp(14), color=Color.TEXT_DARK,
            halign='left', valign='middle', size_hint_x=0.7,
            text_size=(None, dp(36))
        )
        lbl_cnt = Label(
            text=f"[color={','.join(map(str, hit_color[:3]))}][b]总数 {total}  |  命中 {m_cnt}[/b][/color]"
                 if sn_keyword else f"[b]总数 {total}[/b]",
            markup=True, font_size=dp(13), color=Color.TEXT_MUTED,
            halign='right', valign='middle', size_hint_x=0.3,
            text_size=(None, dp(36))
        )
        header.add_widget(lbl_ip)
        header.add_widget(lbl_cnt)
        col.add_widget(header)

        # --- OLT 设备信息 ---
        if olt_detail:
            info_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
            fields = [
                ("型号", olt_detail.get('DT', 'N/A')),
                ("版本", olt_detail.get('DEVER', 'N/A')),
                ("CPU", f"{olt_detail.get('CPU','N/A')}%"),
                ("内存", f"{olt_detail.get('MEM','N/A')}%"),
            ]
            for label, val in fields:
                lbl = Label(
                    text=f"[b]{label}:[/b] {val}",
                    markup=True, font_size=dp(11), color=Color.TEXT_MUTED,
                    halign='left', valign='middle',
                    text_size=(dp(90), dp(26))
                )
                info_row.add_widget(lbl)
            col.add_widget(info_row)

        # --- 分隔线 ---
        sep = BoxLayout(size_hint_y=None, height=dp(1))
        with sep.canvas.before:
            Color(*Color.BORDER)
            Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(pos=lambda *a: setattr(sep.canvas.before.children[-1], 'pos', sep.pos))
        sep.bind(size=lambda *a: setattr(sep.canvas.before.children[-1], 'size', sep.size))
        col.add_widget(sep)

        # --- ONU 列表 ---
        if sn_keyword:
            lbl_hdr = Label(
                text=f"SN 后4位匹配 [{keyword_suffix}]",
                font_size=dp(12), color=Color.TEXT_MUTED,
                size_hint_y=None, height=dp(22), halign='left', valign='middle',
                text_size=(dp(360), dp(22))
            )
            col.add_widget(lbl_hdr)

        for ont in all_onu:
            hit = sn_match(ont.get('SN', ''), sn_keyword)
            item = self._build_onu_item(ont, hit)
            col.add_widget(item)

        if not all_onu:
            lbl_empty = Label(
                text="暂无未注册 ONU", font_size=dp(12),
                color=Color.TEXT_MUTED, size_hint_y=None, height=dp(32),
                halign='center', valign='middle'
            )
            col.add_widget(lbl_empty)

        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=dp(3))
        root.add_widget(col)
        self.add_widget(root)

    def _build_onu_item(self, ont, hit):
        sn = ont.get('SN', 'N/A')
        bg = (0.88, 0.98, 0.90, 1) if hit else (0.97, 0.97, 0.97, 1)
        text_color = (0.10, 0.55, 0.20, 1) if hit else Color.TEXT_DARK

        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(72), padding=[dp(8), dp(4)])
        with item.canvas.before:
            Color(*bg)
            item._bg_rect = Rectangle(pos=item.pos, size=item.size)
        item.bind(pos=self._upd_item, size=self._upd_item)

        # 左：SN码（大字）
        lbl_sn = Label(
            text=f"[b]{sn}[/b]",
            markup=True, font_size=dp(13), color=text_color,
            halign='left', valign='middle', size_hint_x=0.42,
            text_size=(dp(160), dp(72))
        )

        # 中：设备+PON+LOID
        info = BoxLayout(orientation='vertical', size_hint_x=0.38, spacing=dp(2))
        for txt in [
            f"{ont.get('DT','N/A')} · {ont.get('PONID','N/A')}",
            f"LOID: {ont.get('LOID','--') or '--'}",
            f"{ont.get('ERROR','N/A')}"
        ]:
            lbl = Label(
                text=txt, font_size=dp(10), color=Color.TEXT_MUTED,
                halign='left', valign='middle',
                text_size=(dp(130), dp(20))
            )
            info.add_widget(lbl)

        # 右：命中标记
        lbl_hit = Label(
            text="✓ 命中" if hit else "",
            font_size=dp(11), color=(0.13, 0.75, 0.35, 1), bold=True,
            halign='center', valign='middle', size_hint_x=0.20,
            text_size=(dp(50), dp(72))
        )

        item.add_widget(lbl_sn)
        item.add_widget(info)
        item.add_widget(lbl_hit)
        return item

    def _upd_item(self, inst, *args):
        inst._bg_rect.pos = inst.pos
        inst._bg_rect.size = inst.size


# ============================================================
#  主界面
# ============================================================

class MainLayout(BoxLayout):
    orientation = 'vertical'

    def __init__(self, app_ref, **kw):
        super().__init__(**kw)
        self.app_ref = app_ref
        self.padding = 0
        self.spacing = 0
        self.results = []   # 当前结果卡片引用
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---- 顶部标题栏 ----
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56),
            padding=[dp(16), 0], spacing=dp(8)
        )
        with header.canvas.before:
            Color(*Color.PRIMARY)
            header._bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(header._bg, 'pos', header.pos),
                    size=lambda *a: setattr(header._bg, 'size', header.size))

        lbl_title = Label(
            text="🔍 未注册光猫查询", font_size=dp(20), color=Color.TEXT_LIGHT,
            bold=True, halign='left', valign='middle', size_hint_x=1,
            text_size=(dp(300), dp(56))
        )
        header.add_widget(lbl_title)
        self.add_widget(header)

        # ---- 输入区域 ----
        form = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(148),
                         padding=[dp(16), dp(12)], spacing=dp(8))
        with form.canvas.before:
            Color(1, 1, 1, 1)
            form._bg = Rectangle(pos=form.pos, size=form.size)
        form.bind(pos=lambda *a: setattr(form._bg, 'pos', form.pos),
                   size=lambda *a: setattr(form._bg, 'size', form.size))

        # OLT 设备名称
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(46), spacing=dp(10))
        lbl1 = Label(text="设备名称", font_size=dp(14), color=Color.TEXT_DARK,
                     size_hint_x=0.28, halign='left', valign='middle',
                     text_size=(dp(90), dp(46)))
        self.ent_name = TextInput(
            hint_text="输入 OLT 设备名称（支持模糊）", font_size=dp(14),
            multiline=False, write_tab=False, padding=[dp(10), dp(10)],
            size_hint_x=0.72, foreground_color=Color.TEXT_DARK,
            background_color=(0.96, 0.97, 0.99, 1), border=[2, 2, 2, 2]
        )
        row1.add_widget(lbl1)
        row1.add_widget(self.ent_name)

        # SN 码
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(46), spacing=dp(10))
        lbl2 = Label(text="SN 码", font_size=dp(14), color=Color.TEXT_DARK,
                     size_hint_x=0.28, halign='left', valign='middle',
                     text_size=(dp(90), dp(46)))
        self.ent_sn = TextInput(
            hint_text="留空查全部 / 输入取后4位匹配", font_size=dp(14),
            multiline=False, write_tab=False, padding=[dp(10), dp(10)],
            size_hint_x=0.72, foreground_color=Color.TEXT_DARK,
            background_color=(0.96, 0.97, 0.99, 1), border=[2, 2, 2, 2]
        )
        row2.add_widget(lbl2)
        row2.add_widget(self.ent_sn)

        # 按钮行
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(10))

        self.btn_search = Button(
            text="🚀 开始查询", font_size=dp(15), bold=True,
            background_color=(*Color.PRIMARY[:3], 1),
            on_press=self.on_search, size_hint_x=0.65
        )
        self.btn_clear = Button(
            text="清空", font_size=dp(14),
            background_color=(0.60, 0.63, 0.68, 1),
            on_press=self.on_clear, size_hint_x=0.35
        )
        row3.add_widget(self.btn_search)
        row3.add_widget(self.btn_clear)

        form.add_widget(row1)
        form.add_widget(row2)
        form.add_widget(row3)
        self.add_widget(form)

        # ---- 状态栏 ----
        self.lbl_status = Label(
            text="就绪", font_size=dp(12), color=Color.TEXT_MUTED,
            size_hint_y=None, height=dp(30), halign='left', valign='middle',
            text_size=(dp(400), dp(30)), padding=[dp(16), 0]
        )
        self.add_widget(self.lbl_status)

        # ---- 进度条 ----
        self.prog = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(3))
        self.add_widget(self.prog)

        # ---- 结果区域 ----
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False,
                                 bar_width=dp(6), bar_color=(*Color.PRIMARY[:3], 0.6))
        self.results_container = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                                            padding=[dp(12), dp(8)])
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        self.scroll.add_widget(self.results_container)
        self.add_widget(self.scroll)

    # ------------------------------------------------------------------
    def _clear_results(self):
        self.results_container.clear_widgets()
        self.results = []

    def on_clear(self, *args):
        self._clear_results()
        self.lbl_status.text = "已清空"
        self.lbl_status.color = Color.TEXT_MUTED

    def set_status(self, msg, color=None):
        self.lbl_status.text = msg
        self.lbl_status.color = color or Color.TEXT_MUTED

    def set_loading(self, loading):
        self.btn_search.disabled = loading
        if loading:
            Clock.schedule_interval(self._pulse_bar, 0.05)
        else:
            Clock.unschedule(self._pulse_bar)
            self.prog.value = 0

    def _pulse_bar(self, dt):
        v = self.prog.value + 2
        if v > 95:
            v = 0
        self.prog.value = v

    def show_popup(self, title, msg, color=None):
        bg = list(Color.DANGER[:3]) + [1] if color == 'err' else list(Color.INFO[:3]) + [1]
        popup = Popup(
            title=title, content=Label(text=msg, font_size=dp(14), color=Color.TEXT_LIGHT,
                                       text_size=(dp(280), None), valign='middle'),
            size_hint=(0.85, 0.35), auto_dismiss=True,
            title_color=Color.TEXT_LIGHT, title_size=dp(16),
            background_color=bg
        )
        popup.open()

    # ------------------------------------------------------------------
    def on_search(self, *args):
        dev_name = self.ent_name.text.strip()
        sn_keyword = self.ent_sn.text.strip()

        if not dev_name:
            self.show_popup("⚠️ 提示", "请输入 OLT 设备名称")
            return

        self.btn_search.disabled = True
        self._clear_results()
        self.set_status("正在查询...")
        self.set_loading(True)

        t = threading.Thread(target=self._do_search, args=(dev_name, sn_keyword), daemon=True)
        t.start()

    def _do_search(self, dev_name, sn_keyword):
        try:
            ok, result = query_olt_by_name(dev_name)
            if not ok:
                Clock.schedule_once(lambda *a: (
                    self.set_loading(False),
                    self.set_status(f"查询失败: {result}", Color.DANGER),
                    self.show_popup("❌ 查询失败", result, 'err')
                ))
                return

            olt_list = result
            cnt = len(olt_list)
            Clock.schedule_once(lambda *a: self.set_status(f"找到 {cnt} 个 OLT，正在查询 ONU..."))

            if cnt == 1:
                self._query_single(olt_list[0], sn_keyword)
            else:
                with ThreadPoolExecutor(max_workers=min(5, cnt)) as ex:
                    for olt in olt_list:
                        ex.submit(self._query_single, olt, sn_keyword)

            Clock.schedule_once(lambda *a: (
                self.set_loading(False),
                self.set_status("✅ 查询完成", Color.SUCCESS)
            ))

        except Exception as e:
            Clock.schedule_once(lambda *a: (
                self.set_loading(False),
                self.set_status(f"异常: {e}", Color.DANGER),
                self.show_popup("❌ 异常", str(e), 'err')
            ))

    def _query_single(self, olt, sn_keyword):
        olt_ip = olt['ipAddress']
        ems_name = olt['emsName']
        try:
            olt_detail = get_olt_detail(olt_ip, ems_name)
            onu_list = get_onu_list(olt_ip, ems_name)
            matched = [o for o in onu_list if sn_match(o.get('SN', ''), sn_keyword)]

            Clock.schedule_once(
                lambda *a: self._add_card(olt_ip, ems_name, olt_detail, onu_list, matched, sn_keyword)
            )
        except Exception as e:
            Clock.schedule_once(lambda *a: self.set_status(f"OLT {olt_ip} 出错: {e}", Color.DANGER))

    def _add_card(self, olt_ip, ems_name, olt_detail, onu_list, matched, sn_keyword):
        card = OltResultCard(olt_ip, ems_name, olt_detail, onu_list, matched, sn_keyword,
                             size_hint_y=None, height=dp(280 + len(onu_list) * 70))
        self.results_container.add_widget(card)
        self.results.append(card)


# ============================================================
#  App 入口
# ============================================================

class OnuQueryApp(App):
    title = "未注册光猫查询"
    icon = "icon.png"

    def build(self):
        root = BoxLayout(orientation='vertical')
        # 全局背景
        with root.canvas.before:
            Color(*Color.BG)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: (setattr(root._bg, 'pos', root.pos),
                                  setattr(root._bg, 'size', root.size)))
        main = MainLayout(self)
        root.add_widget(main)
        return root


if __name__ in ("__android__", "__main__"):
    OnuQueryApp().run()
