# พจนานุกรมศัพท์ (Glossary) — หนังสือ Leptos ฉบับภาษาไทย

ตารางนี้เป็นคำศัพท์ที่ใช้อย่างสม่ำเสมอตลอดทั้งเล่ม เพื่อให้การแปลทุกบทใช้คำเดียวกัน

| ศัพท์ต้นฉบับ | คำแปลไทย | หมายเหตุ |
|---|---|---|
| signal | สัญญาณ (signal) | หน่วยพื้นฐานของสถานะใน Leptos |
| getter / setter | เก็ตเตอร์ / เซ็ตเตอร์ | |
| `get()` / `set()` / `with()` / `update()` | คงชื่อเมธอดเดิม | |
| reactive / reactivity | รีแอกทีฟ / รีแอกทิวิตี | |
| reactivity graph | กราฟรีแอกทิวิตี | |
| fine-grained reactivity | รีแอกทิวิตีแบบละเอียด (fine-grained) | |
| derived signal | สัญญาณอนุพัทธ์ (derived signal) | |
| memo | เมโม (memo) | |
| effect | เอฟเฟกต์ | |
| disposal | การทิ้ง (disposal) | |
| cleanup | การทำความสะอาด (cleanup) | |
| batch | แบตช์ | |
| component | คอมโพเนนต์ | |
| prop / props | พร็อพ (props) | |
| attribute | แอตทริบิวต์ | |
| attribute spreading | การกระจายแอตทริบิวต์ | |
| element | เอลิเมนต์ | |
| view | วิว (view) | ตัวมาโคร `view!` คงเดิม |
| macro | มาโคร | |
| text node | โหนดข้อความ | |
| DOM | DOM | คงเดิม |
| event listener | ตัวรับฟังเหตุการณ์ (event listener) | |
| event handler | ตัวจัดการเหตุการณ์ (event handler) | |
| closure | โคลเชอร์ | |
| callback | คอลแบ็ก | |
| iterator | อิเทอเรเตอร์ | |
| children | children | คงศัพท์อังกฤษ เพื่อไม่ให้สับสนกับ `<children/>`; ครั้งแรกอธิบายว่า "ลูก (children)" |
| fragment | แฟรกเมนต์ | |
| fallback | ฟอลแบ็ก | |
| Suspense | ซัสเพนส์ (Suspense) | ชื่อคอมโพเนนต์ `<Suspense/>` คงเดิม |
| Transition | ทรานซิชัน (Transition) | ชื่อคอมโพเนนต์ `<Transition/>` คงเดิม |
| action | แอ็กชัน | |
| resource | รีซอร์ส | |
| router | เราเตอร์ | |
| route | เส้นทาง (route) | |
| routing | การจัดเส้นทาง | |
| nested routing | การจัดเส้นทางแบบซ้อน | |
| params | พารามิเตอร์ | |
| queries | ควิรี (queries) | |
| server function | ฟังก์ชันฝั่งเซิร์ฟเวอร์ (server function) | |
| extractor | เอกซ์แทรกเตอร์ | |
| request | คำขอ (request) | |
| response | การตอบกลับ (response) | |
| redirect | การเปลี่ยนเส้นทาง (redirect) | |
| SSR | SSR (คงเดิม) | ขยายความครั้งแรกว่า "การเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR)" |
| CSR | CSR (คงเดิม) | ขยายความครั้งแรกว่า "การเรนเดอร์ฝั่งไคลเอนต์ (CSR)" |
| hydration / hydrate | การไฮเดรต (hydration) / ไฮเดรต | |
| streaming | การสตรีม | |
| islands | เกาะ (islands) | สถาปัตยกรรมแบบเกาะ |
| progressive enhancement | การเสริมความสามารถแบบก้าวหน้า (progressive enhancement) | |
| graceful degradation | การลดทอนอย่างสง่างาม (graceful degradation) | |
| deployment | การดีพลอย | |
| deploy | ดีพลอย | |
| metadata | เมทาดาทา | |
| life cycle | วงจรชีวิต | |
| global state | สถานะส่วนกลาง | |
| context | คอนเท็กซ์ | |
| store | สโตร์ | |
| scope | สโคป | |
| owner / ownership | เจ้าของ / ความเป็นเจ้าของ | |
| trait | แทรต | |
| generic | เจเนอริก | |
| crate | ครีต | |
| compile | คอมไพล์ | |
| compiler | คอมไพเลอร์ | |
| build | บิลด์ | |
| feature flag | ฟีเชอร์แฟล็ก | |
| sandbox | แซนด์บ็อกซ์ | |
| CodeSandbox | CodeSandbox | คงเดิม |
| DevTools | DevTools | คงเดิม |
| `wasm-bindgen` | คงเดิม | ชื่อแพ็กเกจ |
| `web_sys` | คงเดิม | ชื่อครีต |
| `HtmlElement` | คงเดิม | ชื่อชนิดข้อมูล |
| `cargo-leptos` | คงเดิม | ชื่อเครื่องมือ |

## หลักการทั่วไป

- ชื่อเครื่องมือ คำสั่ง CLI ตัวเลือก (flag) ชื่อแพ็กเกจ ครีต ฟังก์ชัน มาโคร และ URL **ไม่แปล** เช่น `cargo-leptos`, `trunk`, `view!`, `signal()`, `wasm-bindgen`
- ชื่อชนิดข้อมูลและ trait ของ Leptos (เช่น `ReadSignal`, `WriteSignal`, `IntoView`, `Mountable`) คงชื่อเดิมตามต้นฉบับ
- โค้ดทุกบล็อก (````rust`, ```sh`, ```toml` ฯลฯ) เก็บไว้ตามต้นฉบับทุกตัวอักษร รวมถึงคอมเมนต์ภายในโค้ด
- บล็อก `admonish` (`note`, `warning`, `info`, `example`, `sandbox` ฯลฯ) แปลข้อความร้อยแก้วและค่า `title=` ได้ แต่คงชื่อ directive และโครงสร้าง HTML/URL เดิมไว้ รวมถึงโค้ดที่ซ้อนอยู่ภายใน
- ลิงก์ (ทั้ง inline และ reference-style) คง path เดิม แปลเฉพาะข้อความที่แสดงผล
- ลิงก์ที่ชี้ไปยังหัวข้อภายในหน้าเดียวกัน (ขึ้นต้นด้วย `#`) ต้องตรวจกับ HTML ที่บิลด์แล้วเสมอ เพราะ mdbook จะแปลงหัวข้อภาษาไทยเป็น slug (เช่น `#การทำงานกับสัญญาณ`) แทน anchor ภาษาอังกฤษเดิม
- ตัวเลือก CLI และชื่อ API อ้างถึงด้วยชื่อเดิมเสมอ (อาจตามด้วยคำแปลในวงเล็บครั้งแรก)
- ใช้ "คุณ" แทน you, "เรา" แทน we/let's ตามโทนของต้นฉบับที่ให้ความเป็นกันเอง
- คงโครงสร้างย่อหน้า หัวข้อ รายการ และ blockquote (`>`) ตามต้นฉบับ; การขึ้นบรรทัดใหม่ภายในย่อหน้าปรับให้อ่านสบายได้
- ตัวเลข วันที่ และเวอร์ชันคงเดิมทุกประการ
