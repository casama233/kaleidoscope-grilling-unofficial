# A1.4.0 轉換與驗證規約

## 來源與輸出分離

原始快照以 Git blob／SHA-256 核對；父模型合併後保存到 `reports/resolved_models/`。內壁處理另存 `reports/export_surfaces/`，不更改來源。編輯 `.bbmodel` 和目標 `.geo.json` 根據同一顯式轉換規格生成，再由不調用轉換器的 `audit_multiview.py` 獨立讀取真實 .geo 驗證。

## 座標和 UV

Java 0–16 方塊座標轉為 Bedrock 中心座標；x 軸映射遵從固定 Blockbench bedrock parse/compile 契約。匯出 origin 為 `[8 - to.x, from.y, from.z - 8]`；pivot 為 `[8 - pivot.x, pivot.y, pivot.z - 8]`。旋轉 x/y 反號，z 不變。原作 texture_size 不直接當成 Java UV 單位；Java UV 始終按原 PNG 尺寸的 1/16 換算。

來源各貼圖在圖集中僅平移，沒有縮放、加濾鏡或預乘 alpha。up/down 面按 Bedrock 契約反轉 UV 的起終端；反向 UV 不以排序數值消除。不同貼圖的原像素含透明RGB均保留。

## 全軸反向內壁

預設檢查仍拒絕負尺寸。只有 spec 明確啟用的全軸反向元素才走 `lower_inward_surfaces`：對原來實際存在的每個面生成原位、單向、零厚度平面，對齊原有頂點與UV的關聯。大缸生成5張、榨油機凹槽生成4張。沒有原有面的地方不補面，沒有新增體积或厚度。

混合軸反向、未知面、未實作的90°／270°面UV旋轉、元素 rescale、未知 tint、非有限值、缺父模型和缺圖仍阻擋。原有零面積面保留在資料中；光柵化時不繪製沒有面積的三角形。

## 驗證邊界

局部結構／引用／數值測試不是完整官方 schema 驗證。有向面集合容差1e-7，保持面繞序與頂點UV對應；只忽略等價的循環起始頂點，不忽略反繞序。原模型與輸出模型分別讀取，使用同一套離線渲染器比較八角度。這不是雙引擎比較。玻璃採近似透明排序，所有引擎材質、姿態、動畫与導入均留待後續。

實際觀察見 `MULTIVIEW-REVIEW.zh-TW.md`。先前A1.1的技術說明另存 `CONVERSION-A11-history.zh-TW.md`，其中「大缸仍阻擋」已由本批顯式拆面規則取代。

## 一手技術依據

- Bedrock geometry schema 1.16：https://learn.microsoft.com/en-us/minecraft/creator/reference/content/schemasreference/schemas/minecraftschema_geometry_1.16.0?view=minecraft-bedrock-stable
- Blockbench固定版本的解析與匯出：https://github.com/JannisX11/blockbench/blob/2569d0245d600030760cf0b8429b1b0017b871f1/js/formats/bedrock/bedrock.js
- 原模組固定提交：https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c

## A1.4.0：180° 面 UV 與粒子引用警告

新增`lower_uv_half_turns`在匯出前將180°面UV改為反向端點，不更改來源快照。這與對矩形四角循環移動兩位等價；支持本批反向UV，90°／270°等仍受阻。輸出維持geometry1.16.0，不依賴`uv_rotation`。每個變換記錄於`uv_lowering`；來源面讀取器獨立解釋Java旋轉，輸出讀取器只讀真正的geo。

`metadata_warnings`報告無法解析的粒子別名，但不以未使用的粒子別名冒充身體貼圖失敗。蘑菇原作`particle="#"`保留，5個分支明列警告。這不是允許身體缺圖：實際面的缺圖／缺引用仍阻擋。

`tests/test_a14.py`包含半轉不改來源、重複執行冪等、反向矩形、非法旋轉阻擋、故意丟失半轉反例，以及舊250份模型／編輯檔／圖集位元組不變檢查。


## A1.7 原生直角面 UV 路徑

顯式 opt-in 的新規格保留 90°／270° 面旋轉，匯出 `uv_rotation`，僅有此欄位的模型升為 1.21.0；.bbmodel 同時保存面 rotation。半轉仍走既有反向端點方案，所以老模型位元組不變。未驗證混合內壁拆面／quarter-turn 的組合繼續阻擋。

官方 schema：https://learn.microsoft.com/en-us/minecraft/creator/reference/content/schemasreference/schemas/minecraftschema_geometry_1.21.0?view=minecraft-bedrock-stable

官方文件規範不等於本工程通過引擎載入，實機驗收仍為未完成。


## A1.8 原始來源與 BOM

建置器以 utf-8-sig 讀取上游 JSON，來源原始 BOM 不刪改。來源 audit 改為另行讀取 pinned snapshots／父模型，不依賴 builder 的 reports/resolved_models。原始父鏈、原 PNG、實際 geo/atlas 與audit程式均納入輸入雜湊。獨立性仍受共用面頂點慣例與光柵器限制。骨肉相連僅十個需要原生直角 UV 的候選用1.21.0；其餘新檔仍1.16.0，旧輸出原位元組不變。
