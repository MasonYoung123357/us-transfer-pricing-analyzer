import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# アプリの基本設定
st.set_page_config(page_title="US Transfer Pricing & IRS Penalty Analyzer", layout="wide")

# 📑 サイドバーで言語切り替え
lang = st.sidebar.radio("Language / 言語選択", ["日本語", "English"])

# 10業界の移転価格ベンチマークデータ、およびIRSの罰則・摘発事例
industry_data = {
    "日本語": {
        "Automotive": {
            "name": "自動車・自動車部品製造",
            "om_range": "3.5% - 6.5%",
            "berry_range": "1.20 - 1.45",
            "plm": "営業利益率 (Operating Margin)",
            "risk": "高リスク：クロスボーダーの金型ライセンス、部品の有償支給、保証費用の配分において、経済的実態と契約の乖離が指摘されやすい。",
            "penalty": "💡 **IRSの罰則・更正例:**\n大手自動車部品メーカーが、海外の子会社へ製造ノウハウを無償許諾していたとして、IRSから5,000万ドルの利益移転を指摘された。IRC §6662(h)に基づく40%の重過失過少申告罰則（Gross Valuation Misstatement Penalty）が適用され、追加税額に加えて2,000万ドルの罰金が科された。"
        },
        "Pharmaceuticals": {
            "name": "製薬・バイオテクノロジー",
            "om_range": "8.0% - 15.0%",
            "berry_range": "1.40 - 1.80",
            "plm": "営業利益率 / 残余利益分割法 (RPSM)",
            "risk": "極めて高リスク：未承認の創薬IP（知的財産）の海外移転や、グローバルR&D費用の分担契約（CSA）におけるプラットフォーム貢献価値の過小評価。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国の製薬巨頭が、タックスヘイブンにある子会社へ特許権を不当に低い価格で売却。IRSは「独立企業原則（Arm's Length Principle）」に反するとして、数年にわたり数十億ドルの利益更正（IRC §482）を行い、同時に移転価格ドキュメンテーションの不備を理由に20%の過少申告罰則を科した（数億ドル規模の和解に発展）。"
        },
        "Semiconductors": {
            "name": "半導体・電子部品製造",
            "om_range": "6.0% - 11.0%",
            "berry_range": "1.30 - 1.60",
            "plm": "営業利益率 / 取引純利益率法 (TNMM)",
            "risk": "高リスク：アジアの受託製造子会社（ファウンドリ）に対する製造委託手数料の設定や、シリコンバレーに集中する設計IPのライセンス料率（ロイヤルティ）の妥当性。",
            "penalty": "💡 **IRSの罰則・更正例:**\n半導体設計会社が、シンガポールの製造・物流拠点に過剰な利益を留保させていた。IRSの監査により、米国の親会社が受け取るべきロイヤルティが過小であると判定。1.2億ドルの所得加算更正とともに、移転価格算定ロジック（§482文書）に重大な欠陥があるとして、20%の罰則（Substantial Valuation Misstatement）が科された。"
        },
        "Software_SaaS": {
            "name": "ソフトウェア & SaaS",
            "om_range": "7.0% - 13.0%",
            "berry_range": "1.35 - 1.70",
            "plm": "取引純利益率法 (TNMM) / 利益分割法",
            "risk": "高リスク：クラウドインフラの運営コスト配分、海外販売子会社（リセラー）に付与する限定的ディストリビューターとしての利益率（LRDモデル）の妥当性。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国SaaS企業がアイルランド子会社を通じて欧州全域へサービスを展開。欧州でのマーケティング活動の本質的な意思決定が米国で行われていたため、IRSはアイルランドへの利益配分が多すぎると主張。移転価格文書のロジックが不十分であったため、罰則軽減（Penalty Relief）が認められず、税額の20%のペナルティが課された。"
        },
        "Medical_Devices": {
            "name": "医療機器製造・販売",
            "om_range": "5.5% - 9.5%",
            "berry_range": "1.25 - 1.55",
            "plm": "営業利益率 (Operating Margin)",
            "risk": "中〜高リスク：海外市場における現地規制対応や臨床試験の費用負担関係、および現地子会社への製品販売価格（再販売価格基準法に準ずる検証）。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国の医療機器メーカーがプエルトリコの製造子会社から不当に高い価格で製品を買い戻していた事例。IRSは「プエルトリコ拠点は単なる受託製造であり、高利益を得る正当性がない」と判断。3億ドルの利益更正を行い、意図的な租税回避とみなされ40%の重罰則が適用された。"
        },
        "Consumer_Electronics": {
            "name": "家電・民生用電子機器ディストリビューション",
            "om_range": "2.0% - 4.5%",
            "berry_range": "1.10 - 1.25",
            "plm": "再販売価格基準法 (RPM) / ベリー比率",
            "risk": "中リスク：海外親会社から製品を輸入する米国販売子会社の利益率。売上高に対するマーケティング費用（AMP費用）の負担が、限定的機能の範囲を超えているかどうかが焦点。",
            "penalty": "💡 **IRSの罰則・更正例:**\nアジアの家電大手の米国販売子会社が、米国市場での激しい競争を理由に複数年赤字を計上。IRSは、米国法人が行う過度な広告宣伝費（AMP費用）を海外親会社が補填すべきと指摘（経済的実態の否認）。米国法人の利益率をレンジ下限（2.0%）まで引き上げる更正を行い、1,500万ドルの追徴税と20%のペナルティを科した。"
        },
        "Retail_E_commerce": {
            "name": "小売・一般消費財 eコマース",
            "om_range": "1.5% - 4.0%",
            "berry_range": "1.08 - 1.22",
            "plm": "ベリー比率 (Berry Ratio) / 営業利益率",
            "risk": "低〜中リスク：グローバル調達網における海外のバイヤー子会社への手数料設定。物流拠点・倉庫の保管リスクや関税との整合性。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国の大手アパレルeコマース企業が、ケイマン諸島の調達子会社に仕入れ価格を上乗せさせ、米国の課税所得を圧縮。IRSのデータ分析（ベンチマーク検証）により、ケイマン法人のベリー比率が業界平均を大幅に逸脱していることが発覚。取引の経済的合理性が否定され、追徴税額に対して20%の過少申告罰則が適用された。"
        },
        "Chemicals": {
            "name": "化学・素材産業製造",
            "om_range": "4.5% - 8.0%",
            "berry_range": "1.20 - 1.40",
            "plm": "独立価格比準法 (CUP) / 営業利益率",
            "risk": "中リスク：コモディティ化学品のインターカンパニー（グループ間）取引における国際市況価格との乖離。特殊化学品の製法ライセンス。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国化学メーカーが、テキサス工場で製造した中間体を欧州の製造子会社に販売。インターカンパニー価格が公開市場価格よりも著しく低かったため、IRSはCUP法（独立価格比準法）を用いて価格を再計算。4,000万ドルの所得加算に加え、企業が§482に基づく移転価格同時文書を期限内に提出していなかったため、一切の罰則免除（Penalty Relief）を受けられず20%の罰則が即時確定した。"
        },
        "Logistics_SupplyChain": {
            "name": "物流・サプライチェーンマネジメントサービス",
            "om_range": "3.0% - 5.5%",
            "berry_range": "1.12 - 1.28",
            "plm": "原価基準法 (Cost Plus Method)",
            "risk": "低〜中リスク：グループ内物流、フォワーディング、通関業務におけるマークアップ（原価上乗せ率）の妥当性。本社費用の海外配分（マネジメントフィー）。",
            "penalty": "💡 **IRSの罰則・更正例:**\nグローバル物流企業の米国本社が、海外子会社に提供した共有ITシステムおよび統括管理サービス（HQシェアードサービス）の費用について、マークアップなしの原価のみで請求していた。IRSは「独立企業間であれば利益を上乗せするサービスである」として、5%のマークアップを強制。所得更正とともに20%の税務ペナルティを科した。"
        },
        "Energy_OilGas": {
            "name": "エネルギー・石油・天然ガス",
            "om_range": "5.0% - 10.0%",
            "berry_range": "1.15 - 1.35",
            "plm": "独立価格比準法 (CUP) / 利益分割法",
            "risk": "高リスク：探鉱・採掘ライセンスのグループ間売買、海上輸送船のチャーターレート（傭船料）、およびデリバティブを用いたグループ内ヘッジ取引の価格設定。",
            "penalty": "💡 **IRSの罰則・更正例:**\n米国のエネルギー企業が、海外の資源開発子会社からの原油購入価格をインデックス価格より高く設定。IRSは、この取引により米国の精製部門の利益が不当に圧縮されていると主張。大規模な監査により数億ドルの利益更正が実施され、企業側の事前価格取り決め（APA）の違反を理由に、IRC §6662に基づく過少申告罰則が最大40%の比率で適用された。"
        }
    },
    "English": {
        "Automotive": {
            "name": "Automotive & Auto Parts Manufacturing",
            "om_range": "3.5% - 6.5%",
            "berry_range": "1.20 - 1.45",
            "plm": "Operating Margin (OM)",
            "risk": "High Risk: Discrepancies between economic substance and contractual terms in cross-border tooling licenses, buy-sell components, and warranty expense allocations.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA major tier-1 auto parts supplier granted manufacturing know-how to its Mexican subsidiary without charging a royalty. The IRS adjusted the US parent's income upward by $50M under IRC §482. Because the company failed to provide adequate contemporary transfer pricing documentation, the IRS imposed a 40% Gross Valuation Misstatement penalty under IRC §6662(h), adding $20M in penalties on top of the back taxes."
        },
        "Pharmaceuticals": {
            "name": "Pharmaceuticals & Biotechnology",
            "om_range": "8.0% - 15.0%",
            "berry_range": "1.40 - 1.80",
            "plm": "Operating Margin / Residual Profit Split Method (RPSM)",
            "risk": "Extremely High Risk: Outbound transfer of unapproved drug IP, or undervaluation of platform contributions in global Cost Sharing Agreements (CSA).",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA US pharma giant transferred blockbuster drug patents to a low-tax European subsidiary at an artificially low buy-in valuation. The IRS determined that the transaction violated the arm's-length principle and reallocated billions in profits over a 5-year audit cycle. The IRS asserted a 20% Substantial Valuation Misstatement penalty due to the lack of robust economic backing in the initial valuation report, resulting in a multi-hundred-million-dollar settlement."
        },
        "Semiconductors": {
            "name": "Semiconductors & Electronic Components",
            "om_range": "6.0% - 11.0%",
            "berry_range": "1.30 - 1.60",
            "plm": "Transactional Net Margin Method (TNMM)",
            "risk": "High Risk: Fabrication pricing for offshore contract manufacturing nodes (foundries) and the arm's-length character of R&D design royalties sent to Silicon Valley parents.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA semiconductor firm funneled excessive profits into its chip packaging and test subsidiary in Singapore. The IRS audited the transaction, ruling that the royalty paid to the US parent for core IP was heavily understated. The IRS issued a $120M adjustments notice along with a 20% penalty, pointing out that the firm's §482 economic benchmarking failed to look at comparable risk profiles."
        },
        "Software_SaaS": {
            "name": "Software & SaaS (Software as a Service)",
            "om_range": "7.0% - 13.0%",
            "berry_range": "1.35 - 1.70",
            "plm": "TNMM / Profit Split Method",
            "risk": "High Risk: Cloud infrastructure cost allocation matrices and testing the profit margins of offshore Limited Risk Distributors (LRD) or localization hubs.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA US SaaS unicorn established an Irish hub to sell subscriptions to the EMEA region. While the software development and executive decisions remained in California, the company allocated 70% of the net margin to Ireland. The IRS rejected the structure, stating the Irish hub was a routine distributor. The company was hit with a 20% underpayment penalty because their internal benchmark didn't account for the 'DEMPE' (Development, Enhancement, Maintenance, Protection, and Exploitation) functions performed in the US."
        },
        "Medical_Devices": {
            "name": "Medical Devices & Equipment",
            "om_range": "5.5% - 9.5%",
            "berry_range": "1.25 - 1.55",
            "plm": "Operating Margin (OM)",
            "risk": "Medium-High Risk: Reimbursement cost sharing for offshore clinical trials and validating transfer pricing for inbound product sales using the Resale Price Method.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA US medical technology firm purchased finished components from its manufacturing facility in Puerto Rico at heavily inflated prices to lower US domestic taxes. The IRS recharacterized the Puerto Rican operation as a routine contract manufacturer rather than an entrepreneurial entity. This led to a $300M profit reallocation to the US parent, accompanied by a 40% gross valuation penalty for intentional profit shifting."
        },
        "Consumer_Electronics": {
            "name": "Consumer Electronics Distribution",
            "om_range": "2.0% - 4.5%",
            "berry_range": "1.10 - 1.25",
            "plm": "Resale Price Method (RPM) / Berry Ratio",
            "risk": "Medium Risk: Inbound distribution margins for US subsidiaries of foreign parents. Excessive local marketing (AMP expenses) spent without reimbursement.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nThe US sales subsidiary of a foreign electronics manufacturer posted consecutive losses, blaming US retail competition. The IRS argued that the US entity acted as an entrepreneurial market builder by spending massively on marketing (AMP expenses) and should have been insulated from losses by the parent. The IRS adjusted the US margin to the arm's-length lower bound (2.0%), issuing a $15M tax deficiency and a 20% §6662 accuracy-related penalty."
        },
        "Retail_E_commerce": {
            "name": "Retail & Consumer Goods E-commerce",
            "om_range": "1.5% - 4.0%",
            "berry_range": "1.08 - 1.22",
            "plm": "Berry Ratio / Operating Margin",
            "risk": "Low-Medium Risk: Commission structures for offshore procurement offices. Aligning risk allocation with warehouse inventory risk and customs valuation.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA US apparel e-retailer routed all Asian manufacturing procurement through a Cayman Islands sourcing shell company, inflating the cost of goods sold in the US. IRS data analysis revealed the Cayman entity's Berry Ratio was 4.0x, vastly higher than the routine sourcing benchmark. The IRS adjusted the transaction, denied the offshore markup, and applied a 20% accuracy penalty for substantial valuation misstatement."
        },
        "Chemicals": {
            "name": "Chemicals & Materials Manufacturing",
            "om_range": "4.5% - 8.0%",
            "berry_range": "1.20 - 1.40",
            "plm": "Comparable Uncontrolled Price (CUP) / OM",
            "risk": "Medium Risk: Deviations from global market index prices in intercompany commodity chemical sales. Valuation of bespoke formulation processes.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA chemical manufacturer sold raw intermediates produced at its Texas plant to a European sister plant at below-market rates. The IRS used the CUP method to readjust the pricing to match publicly traded market indexes. Because the taxpayer failed to produce contemporaneous transfer pricing reports within 30 days of the IRS request, they were denied 'Penalty Relief,' resulting in an immediate 20% underpayment penalty on a $40M adjustment."
        },
        "Logistics_SupplyChain": {
            "name": "Logistics & Supply Chain Services",
            "om_range": "3.0% - 5.5%",
            "berry_range": "1.12 - 1.28",
            "plm": "Cost Plus Method",
            "risk": "Low-Medium Risk: Markup percentages on global freight forwarding, customs clearance, and allocation of corporate headquarters overhead (management fees).",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA global shipping provider's US HQ provided centralized tracking software and regional management to global affiliates at pure cost, without a markup. The IRS maintained that an independent provider would demand a profit. The IRS forced a 5% markup on the corporate services, causing a taxable income increase. The company paid a 20% negligence penalty for failing to evaluate group service agreements under §1.482-9 rules."
        },
        "Energy_OilGas": {
            "name": "Energy, Oil & Gas",
            "om_range": "5.0% - 10.0%",
            "berry_range": "1.15 - 1.35",
            "plm": "CUP Method / Profit Split Method",
            "risk": "High Risk: Intercompany charter rates for shipping vessels, pricing of exploration exploration rights, and cross-border hedging using internal financial derivatives.",
            "penalty": "💡 **IRS Case & Penalty Example:**\nA US oil conglomerate purchased unrefined crude from its foreign extraction subsidiary at prices higher than the spot index, lowering its US refining profits. Following a massive multi-year audit, the IRS adjusted the transfer prices down to the market index. The IRS disallowed the company’s Advanced Pricing Agreement (APA) protections due to critical deviations from the agreed-upon economic facts, enforcing an aggressive 40% gross valuation misstatement penalty."
        }
    }
}[lang]

# 言語辞書の設定
t = {
    "日本語": {
        "title": "🏛️ 米国移転価格（Transfer Pricing）＆IRS罰則アナライザー",
        "caption": "米国における主要業界の独立企業間価格（Arm's Length Range）基準、および内国歳入庁（IRS）によるIRC §6662の罰則・摘発事例を検索・分析する実務ツールです。",
        "sidebar_label": "分析対象の業界を選択してください",
        "header_benchmark": "📊 移転価格 ベンチマーク指標 (Arm's Length Range)",
        "lbl_om": "営業利益率 (Operating Margin Range)",
        "lbl_om_desc": "売上高に対する営業利益の比率（製造業やフル機能ディストリビューターで多用）",
        "lbl_berry": "ベリー比率 (Berry Ratio Range)",
        "lbl_berry_desc": "売上総利益 / 営業費用（販管費）。限定的機能ディストリビューター（LRD）やロジスティクス拠点の検証に有効",
        "lbl_plm": "推奨される主な利益指標 (PLM)",
        "header_risk": "⚠️ この業界における税務リスク・論点",
        "header_penalty": "⚖️ IRS（内国歳入庁）による更正・ペナルティ事例 (IRC §6662)",
        "penalty_notice": "※米国税法上、移転価格ドキュメンテーション（同時文書化）に重大な不備があり、実際の取引価格が基準から大きく逸脱していた場合、過少申告額に対して **20%（重大な逸脱）** または **40%（著しい逸脱）** の精度関連罰則（Accuracy-Related Penalty）が自動的に科されます。"
    },
    "English": {
        "title": "🏛️ US Transfer Pricing & IRS Penalty Analyzer",
        "caption": "A practitioner's tool to evaluate Arm's Length Ranges for US industries, and review real-world IRS audit case studies under IRC §6662.",
        "sidebar_label": "Select Industry Focus Area",
        "header_benchmark": "📊 Arm's Length Range Benchmarks",
        "lbl_om": "Operating Margin (OM) Range",
        "lbl_om_desc": "Operating Income divided by Revenue. Standard for manufacturers and full-fledged buy-sell distributors.",
        "lbl_berry": "Berry Ratio Range",
        "lbl_berry_desc": "Gross Profit divided by Operating Expenses. Highly applicable for Limited Risk Distributors (LRD) and logistics agents.",
        "lbl_plm": "Primary Profit Level Indicator (PLI)",
        "header_risk": "⚠️ Industry Transfer Pricing Risks & Core Issues",
        "header_penalty": "⚖️ Real IRS Audit, Adjustment & Penalty Case Studies (IRC §6662)",
        "penalty_notice": "Note: Under US IRC §6662, if contemporaneous transfer pricing documentation is inadequate and the transfer prices significantly deviate from arm's-length standards, the IRS automatically applies an Accuracy-Related Penalty of either **20% (Substantial Valuation Misstatement)** or **40% (Gross Valuation Misstatement)** on the underpaid tax."
    }
}[lang]

st.title(t["title"])
st.caption(t["caption"])

# サイドバーでの業界選択
industry_keys = list(industry_data["English"].keys())
industry_labels = [industry_data[lang][k]["name"] for k in industry_keys]

selected_label = st.sidebar.selectbox(t["sidebar_label"], industry_labels)
selected_key = industry_keys[industry_labels.index(selected_label)]

selected_industry = industry_data[lang][selected_key]

st.write("---")
st.header(f"🏢 {selected_industry['name']}")

# 📊 基準レンジ表示セクション
st.subheader(t["header_benchmark"])
col1, col2 = st.columns(2)

with col1:
    st.metric(t["lbl_om"], selected_industry["om_range"])
    st.caption(t["lbl_om_desc"])

with col2:
    st.metric(t["lbl_berry"], selected_industry["berry_range"])
    st.caption(t["lbl_berry_desc"])

st.markdown(f"**{t['lbl_plm']}:** `{selected_industry['plm']}`")

# 📊 レンジのビジュアル化（Plotlyグラフ）
om_min = float(selected_industry["om_range"].split("%")[0].split("-")[0].strip())
om_max = float(selected_industry["om_range"].split("%")[0].split("-")[1].strip())

fig = go.Figure()
fig.add_trace(go.Bar(
    y=[selected_industry["name"]],
    x=[om_max - om_min],
    base=om_min,
    orientation='h',
    name='Arm\'s Length Range',
    marker_color='rgba(46, 204, 113, 0.6)',
    hovertemplate=f"Range: {selected_industry['om_range']}<extra></extra>"
))
fig.update_layout(
    title=f"Operating Margin Range Visualization (%)",
    xaxis=dict(title="Operating Margin (%)", range=[0, max(20, om_max + 5)]),
    yaxis=dict(showticklabels=False),
    height=200,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.write("---")

# ⚠️ リスク解説セクション
st.subheader(t["header_risk"])
st.info(selected_industry["risk"])

st.write("---")

# ⚖️ IRS罰則・更正例セクション
st.subheader(t["header_penalty"])
st.error(selected_industry["penalty"])

st.write("---")
st.caption(t["penalty_notice"])