# คู่มือ: Islands

Leptos 0.5 ได้เปิดตัวฟีเจอร์ใหม่ชื่อ `islands` คู่มือนี้จะพาคุณไปทำความรู้จักฟีเจอร์ islands และแนวคิดหลักที่เกี่ยวข้อง พร้อมทั้งร่วมสร้างแอปเดโมโดยใช้สถาปัตยกรรมแบบเกาะ (Islands Architecture)

## สถาปัตยกรรมแบบเกาะ (Islands)

เฟรมเวิร์ก JavaScript ฝั่งฟรอนต์เอนด์กระแสหลัก (React, Vue, Svelte, Solid, Angular) ล้วนมีจุดเริ่มต้นจากการเป็นเฟรมเวิร์กสำหรับสร้าง Single-Page Application (SPA) ที่เรนเดอร์บนไคลเอนต์ โดยการโหลดหน้าเว็บครั้งแรกจะเรนเดอร์โครงร่าง HTML ออกมา จากนั้นจึงทำ hydration และการเปลี่ยนหน้าหรือนำทางในครั้งถัด ๆ ไปจะถูกจัดการบนไคลเอนต์ทั้งหมด (จึงเรียกว่า “single-page”: ทุกสิ่งเกิดขึ้นจากการโหลดหน้าเว็บเพียงครั้งเดียวจากเซิร์ฟเวอร์ แม้ภายหลังจะมีการทำ client-side routing ก็ตาม) ต่อมาเฟรมเวิร์กเหล่านี้ต่างก็เพิ่มการทำ Server-Side Rendering (SSR) เข้ามา เพื่อปรับปรุงเวลาในการโหลดหน้าแรก เพิ่มประสิทธิภาพด้าน SEO และยกระดับประสบการณ์ผู้ใช้งาน

นั่นหมายความว่าโดยค่าเริ่มต้น ทั้งแอปพลิเคชันจะมีความอินเทอร์แอกทีฟ (interactive) และหมายความว่าโค้ดทั้งแอปพลิเคชันจะต้องถูกส่งไปยังไคลเอนต์ในรูปของ JavaScript เพื่อทำการ hydrate ซึ่งแต่เดิม Leptos ก็ดำเนินตามแนวทางเดียวกันนี้

> คุณสามารถอ่านเพิ่มเติมได้ในบทเกี่ยวกับ[การเรนเดอร์ฝั่งเซิร์ฟเวอร์](./ssr/22_life_cycle.md)

แต่ในทางกลับกัน เราสามารถมองมุมกลับได้เช่นกัน แทนที่จะเริ่มจากการมองว่าทั้งแอปต้องเป็น interactive application เรนเดอร์เป็น HTML บนเซิร์ฟเวอร์ แล้วค่อย hydrate ทั้งหมดในเบราว์เซอร์ เราสามารถเริ่มจากหน้าเว็บที่เป็น HTML ธรรมดา แล้วเลือกเติมความอินเทอร์แอกทีฟเฉพาะบางจุดเล็ก ๆ ลงไป ซึ่งนี่คือรูปแบบดั้งเดิมของเว็บไซต์ยุคก่อนปี 2010: เบราว์เซอร์จะส่งคำขอไปยังเซิร์ฟเวอร์ และได้รับหน้า HTML สมบูรณ์กลับมาทุกครั้งที่เปลี่ยนหน้า หลังจากการกำเนิดของ “Single-Page Application” (SPA) แนวทางดั้งเดิมนี้จึงมักถูกเรียกเปรียบเทียบว่า “Multi-Page Application” (MPA)

คำว่า “สถาปัตยกรรมแบบเกาะ” (islands architecture) จึงเกิดขึ้นมาเพื่ออธิบายแนวทางที่เปรียบเสมือนการเริ่มต้นจาก “ทะเล” ของหน้า HTML ล้วน ๆ ที่เรนเดอร์จากเซิร์ฟเวอร์ แล้วแต้ม “เกาะ” (islands) แห่งความอินเทอร์แอกทีฟกระจายอยู่ตามจุดต่าง ๆ ของหน้าเว็บ

> ### อ่านเพิ่มเติม
>
> เนื้อหาส่วนที่เหลือของคู่มือนี้จะเจาะลึกวิธีการใช้งาน islands ใน Leptos หากคุณต้องการศึกษาแนวคิดนี้ในภาพกว้าง สามารถอ่านเพิ่มเติมได้จากบทความต่อไปนี้:
>
> - Jason Miller, [“Islands Architecture”](https://jasonformat.com/islands-architecture/)
> - Ryan Carniato, [“Islands & Server Components & Resumability, Oh My!”](https://dev.to/this-is-learning/islands-server-components-resumability-oh-my-319d)
> - [“Islands Architecture”](https://www.patterns.dev/posts/islands-architecture) บน patterns.dev
> - [Astro Islands](https://docs.astro.build/en/concepts/islands/)

## การเปิดใช้งานโหมด Islands

เรามาเริ่มต้นสร้างแอปด้วย `cargo-leptos` กัน:

```bash
cargo leptos new --git leptos-rs/start-axum
```

> ในตัวอย่างนี้ ทั้ง Actix และ Axum แทบไม่มีความแตกต่างกัน

ระหว่างนี้สามารถสั่งรัน

```bash
cargo leptos build
```

ทิ้งไว้เป็นเบื้องหลัง แล้วเปิดโค้ดในเอดิเตอร์เพื่อเริ่มปรับแต่งได้เลย

สิ่งแรกที่ต้องทำคือเพิ่มฟีเจอร์ `islands` ในไฟล์ `Cargo.toml` โดยเพิ่มเข้าไปที่เครต `leptos` เพียงตัวเดียว:

```toml
leptos = { version = "0.7", features = ["islands"] }
```

ถัดไป ให้แก้ไขฟังก์ชัน `hydrate` ที่เอ็กซ์พอร์ตอยู่ใน `src/lib.rs` โดยลบบรรทัดที่เรียก `leptos::mount::hydrate_body(App)` แล้วแทนที่ด้วย:

```rust
leptos::mount::hydrate_islands();
```

แทนที่จะรันทั้งแอปพลิเคชันและ hydrate view ทั้งหมดที่ถูกสร้างขึ้น วิธีนี้จะเลือก hydrate แต่ละเกาะแยกกันทีละอันตามลำดับ

และในไฟล์ `app.rs` ภายในฟังก์ชัน `shell` เราต้องเพิ่ม `islands=true` ให้กับคอมโพเนนต์ `HydrationScripts` ด้วยเช่นกัน:

```rust
<HydrationScripts options islands=true/>
```

ทีนี้ลองรัน `cargo leptos watch` แล้วเปิดเบราว์เซอร์ไปที่ [`http://localhost:3000`](http://localhost:3000)

ลองคลิกที่ปุ่มดู แล้วจะพบว่า...

ไม่มีอะไรเกิดขึ้นเลย!

ยอดเยี่ยม ถูกต้องตามแผนแล้ว

```admonish note
ในเทมเพลตเริ่มต้นจะมีบรรทัด `use app::*;` อยู่ในนิยามของฟังก์ชัน `hydrate()` แต่เมื่อเปลี่ยนมาใช้โหมด islands คุณไม่ได้เรียกใช้คอมโพเนนต์หลัก `App` ที่อิมพอร์ตเข้ามาอีกต่อไป คุณอาจคิดว่าสามารถลบบรรทัดนี้ทิ้งได้ (และจริง ๆ แล้ว linter ของ Rust ก็อาจจะแจ้งเตือนให้ลบด้วย!)

อย่างไรก็ตาม การลบบรรทัดนี้อาจทำให้เกิดปัญหาได้หากคุณใช้โครงสร้างโปรเจกต์แบบ Cargo workspace เนื่องจากเราใช้ `wasm-bindgen` ในการเอ็กซ์พอร์ต entrypoint แยกต่างหากสำหรับแต่ละฟังก์ชัน จากประสบการณ์พบว่า หากอยู่ใน workspace แล้วไม่มีโค้ดใดในเครต `frontend` เรียกใช้เครต `app` เลย ตัว bindings เหล่านั้นจะไม่ถูกสร้างขึ้นอย่างสมบูรณ์ [สามารถอ่านบทสนทนานี้เพิ่มเติมได้](https://github.com/leptos-rs/leptos/issues/2083#issuecomment-1868053733)
```

## การใช้งาน Islands

สาเหตุที่ไม่มีอะไรเกิดขึ้น ก็เพราะเราเพิ่งพลิก mental model ของแอปพลิเคชันใหม่ทั้งหมด แทนที่จะตั้งต้นว่าทั้งแอปต้องเป็น interactive และคอย hydrate ทุกสิ่ง ตอนนี้หน้าเว็บทั้งหมดจะกลายเป็น HTML นิ่ง ๆ โดยค่าเริ่มต้น และเราต้องเป็นผู้กำหนดจุดที่ต้องการความอินเทอร์แอกทีฟด้วยตนเอง

สิ่งนี้ส่งผลต่อขนาดของไบนารี WASM อย่างมหาศาล: หากคอมไพล์ในโหมด release แอปนี้จะมีขนาด WASM เพียง 24kb เท่านั้น (แบบยังไม่บีบอัด) เมื่อเทียบกับ 274kb ในโหมดปกติที่ไม่ใช่ islands (274kb ถือว่าค่อนข้างใหญ่สำหรับหน้า “Hello, world!” ซึ่งจริง ๆ แล้วส่วนใหญ่คือโค้ดทั้งหมดที่เกี่ยวข้องกับ client-side routing ที่ไม่ได้ถูกใช้งานในเดโมนี้เลย)

เมื่อคลิกปุ่มแล้วไม่มีอะไรตอบสนอง เพราะทั้งหน้าเว็บกลายเป็นเนื้อหาสถิต (static) ไปแล้ว

แล้วเราจะทำให้มันกลับมามีลูกเล่นอินเทอร์แอกทีฟได้อย่างไร?

คำตอบคือ เปลี่ยนคอมโพเนนต์ `HomePage` ให้กลายเป็นเกาะ (island) นั่นเอง!

นี่คือเวอร์ชันที่ไม่เป็นอินเทอร์แอกทีฟ:

```rust
#[component]
fn HomePage() -> impl IntoView {
    // Creates a reactive value to update the button
    let count = RwSignal::new(0);
    let on_click = move |_| *count.write() += 1;

    view! {
        <h1>"Welcome to Leptos!"</h1>
        <button on:click=on_click>"Click Me: " {count}</button>
    }
}
```

นี่คือเวอร์ชันที่เป็นอินเทอร์แอกทีฟ:

```rust
#[island]
fn HomePage() -> impl IntoView {
    // Creates a reactive value to update the button
    let count = RwSignal::new(0);
    let on_click = move |_| *count.write() += 1;

    view! {
        <h1>"Welcome to Leptos!"</h1>
        <button on:click=on_click>"Click Me: " {count}</button>
    }
}
```

ตอนนี้เมื่อลองคลิกปุ่มอีกครั้ง ปุ่มก็กลับมาทำงานได้แล้ว!

มาโคร `#[island]` ทำงานเหมือนกับมาโคร `#[component]` ทุกประการ ข้อแตกต่างเพียงอย่างเดียวคือ เมื่ออยู่ในโหมด islands ตัวมาโครนี้จะระบุว่าคอมโพเนนต์ดังกล่าวคือเกาะที่มีความอินเทอร์แอกทีฟ หากเราตรวจดูขนาดไบนารี WASM อีกครั้ง ในโหมด release จะอยู่ที่ 166kb (แบบไม่บีบอัด) ซึ่งแม้จะใหญ่กว่าเวอร์ชัน static ล้วนที่ 24kb แต่ก็เล็กกว่าเวอร์ชันแบบ full-hydration ที่มีขนาดถึง 355kb อยู่มาก

หากคุณเปิดดูซอร์สโค้ด HTML ของหน้าเว็บในเบราว์เซอร์ จะเห็นว่าเกาะ `HomePage` ถูกเรนเดอร์ออกมาเป็น custom HTML element ชื่อ `<leptos-island>` ซึ่งจะระบุว่าควรใช้คอมโพเนนต์ใดในการทำ hydrate:

```html
<leptos-island data-component="HomePage_7432294943247405892">
  <h1>Welcome to Leptos!</h1>
  <button>
    Click Me:
    <!>0
  </button>
</leptos-island>
```

มีเพียงโค้ดที่อยู่ภายใน `<leptos-island>` นี้เท่านั้นที่จะถูกคอมไพล์ลงใน WASM และมีเพียงโค้ดส่วนนี้เท่านั้นที่จะถูกรันระหว่างขั้นตอนการ hydrate

## การใช้งาน Islands อย่างมีประสิทธิภาพ

โปรดระลึกไว้ว่ามี _เฉพาะ_ โค้ดที่อยู่ภายใน `#[island]` เท่านั้นที่ต้องถูกคอมไพล์เป็น WASM แล้วส่งไปยังเบราว์เซอร์ นั่นหมายความว่าเราควรออกแบบเกาะให้มีขนาดเล็กและเฉพาะเจาะจงที่สุดเท่าที่จะเป็นไปได้ ตัวอย่างเช่น `HomePage` จะดียิ่งขึ้นหากเราแยกโครงร่างทั่วไปออกเป็นคอมโพเนนต์ปกติ แล้วแยกเฉพาะตัวนับออกมาเป็นเกาะ:

```rust
#[component]
fn HomePage() -> impl IntoView {
    view! {
        <h1>"Welcome to Leptos!"</h1>
        <Counter/>
    }
}

#[island]
fn Counter() -> impl IntoView {
    // Creates a reactive value to update the button
    let (count, set_count) = signal(0);
    let on_click = move |_| *set_count.write() += 1;

    view! {
        <button on:click=on_click>"Click Me: " {count}</button>
    }
}
```

เพียงเท่านี้ แท็ก `<h1>` ก็ไม่จำเป็นต้องถูกรวมเข้าไปในไคลเอนต์บันเดิล และไม่ต้องผ่านกระบวนการ hydrate แม้ดูเหมือนจะเป็นการปรับปรุงเพียงเล็กน้อย แต่ลองนึกภาพว่าคุณสามารถเพิ่มเนื้อหา HTML สถิตลงใน `HomePage` ได้มากเท่าที่ต้องการ โดยที่ขนาดของไบนารี WASM จะไม่ขยับเพิ่มขึ้นแม้แต่น้อย

ในโหมด hydration ปกติ ขนาดไบนารี WASM จะโตขึ้นตามขนาดและความซับซ้อนของทั้งแอปพลิเคชัน แต่ในโหมด islands ขนาดไบนารี WASM จะเติบโตตามปริมาณของความอินเทอร์แอกทีฟที่มีอยู่ในแอปเท่านั้น คุณสามารถเพิ่มเนื้อหา static นอกเกาะได้มากเท่าที่ต้องการโดยไม่ส่งผลกระทบต่อขนาดของไบนารีเลย

## ปลดล็อกพลังพิเศษ

การลดขนาดไบนารี WASM ลงได้ถึง 50% เป็นเรื่องที่ยอดเยี่ยม แต่ประโยชน์ที่แท้จริงไม่ได้หยุดอยู่แค่นั้น

ความทรงพลังที่แท้จริงจะปรากฏชัดเมื่อคุณผสานข้อเท็จจริงสำคัญสองประการเข้าด้วยกัน:

1. โค้ดภายในฟังก์ชัน `#[component]` จะทำงานบนเซิร์ฟเวอร์ _เท่านั้น_ เว้นแต่คุณจะนำไปเรียกใช้ภายในเกาะ\*
2. children และ prop ต่าง ๆ สามารถส่งจากเซิร์ฟเวอร์เข้าไปในเกาะได้ โดยไม่ต้องถูกรวมไว้ในไบนารี WASM เลย

นั่นหมายความว่าคุณสามารถเขียนโค้ดที่ทำงานเฉพาะบนเซิร์ฟเวอร์ (server-only code) ไว้ในตัวคอมโพเนนต์ได้โดยตรง แล้วส่งผลลัพธ์ผ่านเข้าไปยัง children ของเกาะ งานหลายอย่างที่เดิมเคยต้องใช้ความซับซ้อนของการผสมผสานระหว่าง server function และ `Suspense` ในแอปแบบ full-hydration ตอนนี้สามารถเขียนแบบ inline ได้ง่ายดายทันที

> \* ข้อความที่ว่า “เว้นแต่คุณจะนำไปเรียกใช้ภายในเกาะ” นั้นสำคัญมาก เพราะ _ไม่ใช่_ ว่าทุก `#[component]` จะถูกบังคับให้รันบนเซิร์ฟเวอร์เท่านั้น หากแต่พวกมันเป็น “shared component” ที่จะถูกคอมไพล์ลงในไบนารี WASM ก็ต่อเมื่อถูกเรียกใช้ภายในบอดี้ของ `#[island]` เท่านั้น แต่หากไม่ได้เรียกใช้ในเกาะ โค้ดเหล่านั้นก็จะไม่ถูกส่งไปรันบนเบราว์เซอร์เลย

และเรายังจะใช้ประโยชน์จากข้อเท็จจริงประการที่สามในตัวอย่างถัดไป:

3. context สามารถส่งต่อระหว่างเกาะต่าง ๆ ที่ทำงานเป็นอิสระต่อกันได้

ดังนั้น แทนที่จะหยุดอยู่แค่ตัวอย่างปุ่มนับเลข เรามาลองสร้างอะไรที่สนุกและสมจริงยิ่งขึ้น: อินเทอร์เฟซระบบแท็บ (tabs) ที่อ่านข้อมูลเนื้อหาจากไฟล์บนเซิร์ฟเวอร์โดยตรง

## การส่ง children ฝั่งเซิร์ฟเวอร์ให้ Islands

หนึ่งในคุณสมบัติที่ยอดเยี่ยมที่สุดของสถาปัตยกรรม islands คือคุณสามารถส่ง children ที่เรนเดอร์จากเซิร์ฟเวอร์เข้าไปในเกาะได้ โดยที่ตัวเกาะไม่จำเป็นต้องรู้รายละเอียดใด ๆ เกี่ยวกับ children เหล่านั้นเลย ตัวเกาะจะทำการ hydrate เฉพาะเนื้อหาภายในของมันเอง แต่จะไม่ไปแตะต้อง children ฝั่งเซิร์ฟเวอร์ที่ถูกส่งเข้ามา

ดังที่ Dan Abramov (ทีมพัฒนา React) ได้เคยเปรียบเปรยไว้ในบริบทของ React Server Components (RSC) ว่า แท้จริงแล้วเกาะไม่ได้มีลักษณะเหมือนเกาะ แต่เหมือนกับ “โดนัท” มากกว่า คุณสามารถส่งเนื้อหาฝั่งเซิร์ฟเวอร์ล้วน ๆ สอดแทรกเข้าไปใน “รูตรงกลางของโดนัท” ได้โดยตรง ทำให้คุณสามารถสร้างเกาะแห่งความอินเทอร์แอกทีฟที่ถูกโอบล้อมด้วยทะเลของ HTML สถิตจากเซิร์ฟเวอร์ทั้งภายนอกและภายใน

> ในโค้ดตัวอย่างด้านล่าง เราได้ใส่สไตล์เพื่อเน้นให้เห็นเนื้อหาฝั่งเซิร์ฟเวอร์เป็นสีฟ้าอ่อน (เปรียบเหมือน “น้ำทะเล”) และส่วนของเกาะอินเทอร์แอกทีฟเป็นสีเขียวอ่อน (เปรียบเหมือน “ผืนดิน”) เพื่อช่วยให้เห็นภาพการทำงานได้อย่างชัดเจนยิ่งขึ้น

มาต่อกับเดโมกัน: ผมจะสร้างคอมโพเนนต์ `Tabs` การสลับแท็บจะต้องมีความอินเทอร์แอกทีฟ ดังนั้นแน่นอนว่ามันจะเป็นเกาะ เริ่มง่ายๆ ก่อนตอนนี้:

```rust
#[island]
fn Tabs(labels: Vec<String>) -> impl IntoView {
    let buttons = labels
        .into_iter()
        .map(|label| view! { <button>{label}</button> })
        .collect_view();
    view! {
        <div style="display: flex; width: 100%; justify-content: space-between;">
            {buttons}
        </div>
    }
}
```

อุ๊ปส์ มันให้ข้อผิดพลาดกับผม

```
error[E0463]: can't find crate for `serde`
  --> src/app.rs:43:1
   |
43 | #[island]
   | ^^^^^^^^^ can't find crate
```

แก้ไขง่ายๆ: รัน `cargo add serde --features=derive` มาโคร `#[island]` ต้องการดึง `serde` เข้ามาในกรณีนี้ เพราะมันต้องซีเรียลไลซ์และดีซีเรียลไลซ์พร็อพ `labels`

ตอนนี้มาอัปเดต `HomePage` ให้ใช้ `Tabs` กัน

```rust
#[component]
fn HomePage() -> impl IntoView {
	// these are the files we’re going to read
    let files = ["a.txt", "b.txt", "c.txt"];
	// the tab labels will just be the file names
	let labels = files.iter().copied().map(Into::into).collect();
    view! {
        <h1>"Welcome to Leptos!"</h1>
        <p>"Click any of the tabs below to read a recipe."</p>
        <Tabs labels/>
    }
}
```

ถ้าคุณดูใน DOM inspector คุณจะเห็นว่าเกาะตอนนี้มีลักษณะประมาณนี้

```html
<leptos-island
  data-component="Tabs_1030591929019274801"
  data-props='{"labels":["a.txt","b.txt","c.txt"]}'
>
  <div style="display: flex; width: 100%; justify-content: space-between;;">
    <button>a.txt</button>
    <button>b.txt</button>
    <button>c.txt</button>
    <!---->
  </div>
</leptos-island>
```

พร็อพ `labels` ของเราถูกซีเรียลไลซ์เป็น JSON และเก็บไว้ในแอตทริบิวต์ HTML เพื่อให้สามารถใช้ไฮเดรตเกาะได้

ตอนนี้มาเพิ่มแท็บกันบ้าง ตอนนี้เกาะ `Tab` จะเรียบง่ายมาก:

```rust
#[island]
fn Tab(index: usize, children: Children) -> impl IntoView {
    view! {
        <div>{children()}</div>
    }
}
```

แต่ละแท็บ ตอนนี้จะเป็นแค่ `<div>` ที่ห่อหุ้ม children ของมัน

คอมโพเนนต์ `Tabs` ของเราก็จะได้รับ children ด้วย: ตอนนี้ขอแค่แสดงทั้งหมดก่อน

```rust
#[island]
fn Tabs(labels: Vec<String>, children: Children) -> impl IntoView {
    let buttons = labels
        .into_iter()
        .map(|label| view! { <button>{label}</button> })
        .collect_view();
    view! {
        <div style="display: flex; width: 100%; justify-content: space-around;">
            {buttons}
        </div>
        {children()}
    }
}
```

เอาละ ตอนนี้กลับไปที่ `HomePage` กัน เราจะสร้างรายการแท็บเพื่อใส่ในกล่องแท็บของเรา

```rust
#[component]
fn HomePage() -> impl IntoView {
    let files = ["a.txt", "b.txt", "c.txt"];
    let labels = files.iter().copied().map(Into::into).collect();
	let tabs = move || {
        files
            .into_iter()
            .enumerate()
            .map(|(index, filename)| {
                let content = std::fs::read_to_string(filename).unwrap();
                view! {
                    <Tab index>
                        <h2>{filename.to_string()}</h2>
                        <p>{content}</p>
                    </Tab>
                }
            })
            .collect_view()
    };

    view! {
        <h1>"Welcome to Leptos!"</h1>
        <p>"Click any of the tabs below to read a recipe."</p>
        <Tabs labels>
            <div>{tabs()}</div>
        </Tabs>
    }
}
```

เดี๋ยวนะ... เขียนแบบนี้ได้ด้วยหรือ?

หากคุณคุ้นเคยกับการเขียน Leptos แบบเดิม คุณคงจะแย้งทันทีว่าทำแบบนี้ไม่ได้เด็ดขาด เพราะโค้ดในตัวคอมโพเนนต์จะต้องรันได้ทั้งบนเซิร์ฟเวอร์ (เพื่อเรนเดอร์ HTML) และบนเบราว์เซอร์ (เพื่อทำ hydration) ดังนั้นการเรียกใช้ `std::fs` ดื้อ ๆ แบบนี้จะทำให้โปรแกรม panic บนเบราว์เซอร์อย่างแน่นอน เพราะบนเบราว์เซอร์ไม่มีระบบ filesystem ของเครื่อง (และที่สำคัญคือเข้าถึง filesystem ของเซิร์ฟเวอร์ไม่ได้!) หากทำได้คงกลายเป็นช่องโหว่ด้านความปลอดภัยร้ายแรง!

แต่ช้าก่อน... ตอนนี้เรากำลังอยู่ในโหมด islands และคอมโพเนนต์ `HomePage` นี้ทำงานบนเซิร์ฟเวอร์ _เท่านั้นจริง ๆ_ เราจึงสามารถเรียกใช้โค้ดฝั่งเซิร์ฟเวอร์ธรรมดาแบบนี้ได้โดยตรงโดยไม่ต้องกังวล

> **ตัวอย่างนี้ดูแปลกไปหน่อยไหม?** ใช่แล้ว! การอ่านไฟล์พร้อมกัน 3 ไฟล์แบบ synchronous ใน `.map()` คงไม่ใช่วิธีที่ดีในการพัฒนาแอปจริง แต่เป้าหมายของตัวอย่างนี้คือการพิสูจน์ให้เห็นอย่างชัดเจนว่า นี่คือเนื้อหาที่ทำงานบนฝั่งเซิร์ฟเวอร์อย่างแท้จริง

ลองสร้างไฟล์ 3 ไฟล์ไว้ที่รูทของโปรเจกต์ ชื่อ `a.txt`, `b.txt` และ `c.txt` แล้วใส่ข้อความอะไรก็ได้ลงไป

จากนั้นรีเฟรชหน้าเว็บ คุณจะเห็นเนื้อหาไฟล์แสดงผลบนเบราว์เซอร์ทันที ลองแก้ไขข้อความในไฟล์แล้วรีเฟรชใหม่อีกครั้ง ข้อมูลก็จะอัปเดตตามทันที

คุณสามารถส่งเนื้อหาฝั่งเซิร์ฟเวอร์จาก `#[component]` เข้าไปยัง children ของ `#[island]` ได้ โดยที่ตัวเกาะไม่จำเป็นต้องรู้เลยว่าข้อมูลเหล่านั้นถูกดึงมาอย่างไรหรือเรนเดอร์อย่างไร

**จุดนี้มีความสำคัญเป็นอย่างยิ่ง**: การส่ง `children` ฝั่งเซิร์ฟเวอร์เข้าไปในเกาะช่วยให้คุณสามารถบีบขนาดของเกาะให้เล็กลงได้ ในทางอุดมคติ เราไม่ควรนำ `#[island]` ไปครอบทั้งบล็อกใหญ่ของหน้าเว็บ แต่ควรแยกส่วนอินเทอร์แอกทีฟออกมาเป็น `#[island]` และส่งเนื้อหาส่วนอื่น ๆ ของเซิร์ฟเวอร์เข้าไปเป็น `children` แทน เพื่อตัดโค้ดส่วนที่ไม่มีการโต้ตอบออกจากไบนารี WASM ให้ได้มากที่สุด

## การส่งคอนเท็กซ์ระหว่าง Islands

ตอนนี้ยังไม่ใช่ “แท็บ” จริงๆ มันแค่แสดงทุกแท็บตลอดเวลา ดังนั้นมาเพิ่มลอจิกง่ายๆ ให้คอมโพเนนต์ `Tabs` และ `Tab` กัน

เราจะแก้ `Tabs` ให้สร้างสัญญาณ `selected` ง่ายๆ เรามอบครึ่งที่เป็นการอ่านผ่านคอนเท็กซ์ และตั้งค่าของสัญญาณทุกครั้งที่มีคนคลิกปุ่มของเราสักปุ่ม

```rust
#[island]
fn Tabs(labels: Vec<String>, children: Children) -> impl IntoView {
    let (selected, set_selected) = signal(0);
    provide_context(selected);

    let buttons = labels
        .into_iter()
        .enumerate()
        .map(|(index, label)| view! {
            <button on:click=move |_| set_selected.set(index)>
                {label}
            </button>
        })
        .collect_view();
// ...
```

และมาแก้เกาะ `Tab` ให้ใช้คอนเท็กซ์นั้นเพื่อแสดงหรือซ่อนตัวเอง:

```rust
#[island]
fn Tab(index: usize, children: Children) -> impl IntoView {
    let selected = expect_context::<ReadSignal<usize>>();
    view! {
        <div
            style:background-color="lightgreen"
            style:padding="10px"
            style:display=move || if selected.get() == index {
                "block"
            } else {
                "none"
            }
        >
            {children()}
        </div>
    }
}
```

ตอนนี้ระบบแท็บทำงานได้อย่างถูกต้องสมบูรณ์แล้ว `Tabs` ส่งต่อ signal ผ่าน context ไปยังแต่ละ `Tab` เพื่อให้แต่ละแท็บตัดสินใจว่าจะแสดงผลหรือซ่อนตัวเอง

> นี่คือเหตุผลว่าทำไมใน `HomePage` เราจึงกำหนด `let tabs = move ||` ให้เป็นฟังก์ชัน แล้วเรียกใช้งานด้วย `{tabs()}` เพราะการสร้างแท็บแบบ lazy เช่นนี้ จะช่วยรับประกันว่าเกาะ `Tabs` ได้ประกาศ context `selected` ไว้เรียบร้อยแล้ว ก่อนที่แต่ละ `Tab` ภายในจะเริ่มค้นหา context นั้น

เดโมระบบแท็บที่เสร็จสมบูรณ์นี้มีขนาดประมาณ 200kb (แบบไม่บีบอัด) แม้จะไม่ใช่ขนาดที่เล็กที่สุด แต่ก็เล็กกว่าหน้า “Hello, world” ที่มี client-side router ในตอนแรกอย่างเห็นได้ชัด และเมื่อลองทดสอบบิลด์ระบบเดียวกันนี้โดยไม่ใช้โหมด islands (ใช้ `#[server]` ร่วมกับ `Suspense`) ขนาดจะพุ่งสูงกว่า 400kb ทันที ซึ่งแสดงให้เห็นว่าเราประหยัดขนาดไบนารีลงได้ถึงราว 50% และที่สำคัญคือ แอปนี้ยังมีเนื้อหาฝั่งเซิร์ฟเวอร์อยู่น้อยมาก โปรดจำไว้ว่าแม้คุณจะเพิ่มหน้าเพจหรือคอมโพเนนต์ฝั่งเซิร์ฟเวอร์เข้ามาอีกมากเพียงใด ขนาดไบนารี 200kb นี้ก็จะไม่บวมขึ้นอีกเลย

## การแทนที่เราเตอร์ฝั่งไคลเอนต์

หนึ่งในเป้าหมายหลักของการใช้ islands คือการตัดระบบ routing ออกจากฝั่งไคลเอนต์ เพราะเมื่อมี client-side router คุณจำเป็นต้องคอมไพล์โค้ดสำหรับเรนเดอร์ทุกหน้าเว็บส่งไปให้ไคลเอนต์ การใช้ islands จะช่วยลดปริมาณโค้ดที่ส่งไปยังเบราว์เซอร์ได้อย่างมหาศาล ทว่าก็ต้องแลกมาด้วยการสละความสะดวกสบายบางประการของ client-side routing

อย่างไรก็ตาม ยังมีโหมด "islands router" ที่ผสาน client-side routing เข้ากับ islands โดยอาศัย JavaScript ขนาดเล็กบนฟรอนต์เอนด์เพื่อคอย fetch หน้า HTML ที่เรนเดอร์ใหม่จากเซิร์ฟเวอร์และทำ diff เพื่ออัปเดตหน้าเว็บอย่างมีประสิทธิภาพ คุณสามารถศึกษาเพิ่มเติมได้จาก [ตัวอย่าง `islands_router`](https://github.com/leptos-rs/leptos/tree/main/examples/islands_router) ซึ่งทำงานได้เป็นอย่างดี และรองรับทั้งการนำทางผ่านลิงก์และการส่งฟอร์ม

โปรดทราบว่าหากไม่มี client-side router คุณจะไม่สามารถเรียก `redirect()` จาก server function เพื่อสั่งเปลี่ยนหน้าบนไคลเอนต์ได้โดยตรง เนื่องจากความสามารถนี้ขึ้นอยู่กับเราเตอร์ แต่คุณสามารถสร้าง hook พื้นฐานขึ้นมาเองได้ด้วยการเรียก [`set_redirect_hook`](https://docs.rs/leptos/latest/leptos/server_fn/redirect/fn.set_redirect_hook.html):
```rust
set_redirect_hook(|url| {
    window().location().set_href(url);
});
```
ตอนนี้ ฟังก์ชันฝั่งเซิร์ฟเวอร์ใด ๆ ที่เรียกใช้ `redirect()` ก็จะถูกจัดการบนไคลเอนต์ด้วยการนำทางของเบราว์เซอร์ตามปกติ

## ภาพรวม

แม้ตัวอย่างนี้จะดูเรียบง่าย แต่ก็ให้ข้อคิดและประโยชน์ที่เห็นได้ชัดเจนหลายประการ:

- **ลดขนาดไบนารี WASM ลงถึง 50%**: ช่วยยกระดับเวลาในการเริ่มมีปฏิสัมพันธ์ (Time to Interactive) และลดระยะเวลาการโหลดหน้าแรกของไคลเอนต์ได้อย่างชัดเจน
- **ลดต้นทุนในการ serialize ข้อมูล**: การสร้าง resource แล้วอ่านค่าบนไคลเอนต์จำเป็นต้องแปลงข้อมูล (serialize) เพื่อใช้ในกระบวนการ hydrate และหากคุณอ่านข้อมูลนั้นมาเรนเดอร์เป็น HTML ภายใน `Suspense` ด้วย จะเกิดปัญหา “double data” คือข้อมูลชุดเดียวกันถูกเรนเดอร์เป็นทั้ง HTML และถูก serialize ซ้ำเป็น JSON ใน payload ซึ่งเพิ่มขนาดการตอบกลับและทำให้โหลดช้าลง
- **เรียกใช้ server-only API ได้อย่างง่ายดาย**: ภายใน `#[component]` คุณสามารถเรียกฟังก์ชัน Rust ที่ทำงานบนเซิร์ฟเวอร์ได้โดยตรง เพราะในโหมด islands คอมโพเนนต์เหล่านี้จะรันอยู่บนเซิร์ฟเวอร์จริง ๆ!
- **ลดโค้ด boilerplate ของ `#[server]`/`create_resource`/`Suspense`**: ตัดความยุ่งยากในการดึงข้อมูลจากเซิร์ฟเวอร์ลงไปได้อย่างมาก

## การสำรวจในอนาคต

ฟีเจอร์ `islands` สะท้อนถึงการทดลองในระดับแนวหน้าของวงการเว็บฟรอนต์เอนด์ในปัจจุบัน ในสถานะปัจจุบัน แนวทาง islands ของเรามีความใกล้เคียงกับ Astro มาก (ก่อนที่จะมีการเพิ่ม View Transitions ในเวอร์ชันล่าสุด) โดยช่วยให้คุณสร้างแอปพลิเคชันแบบ multi-page ดั้งเดิมที่เรนเดอร์บนเซิร์ฟเวอร์ แล้วผสานเกาะอินเทอร์แอกทีฟเข้าไปได้อย่างแนบเนียน

ยังมีการพัฒนาและปรับปรุงอีกหลายส่วนที่สามารถต่อยอดได้ง่าย เช่นเดียวกับแนวทาง View Transitions ของ Astro:

- เพิ่มระบบ client-side routing สำหรับแอป islands โดย fetch การนำทางครั้งถัดไปจากเซิร์ฟเวอร์ แล้วสลับแทนที่เอกสาร HTML ด้วยหน้าใหม่
- เพิ่มแอนิเมชันการเปลี่ยนผ่าน (animated transitions) ระหว่างหน้าเก่าและหน้าใหม่ด้วย View Transitions API
- รองรับ persistent islands อย่างชัดเจน กล่าวคือเกาะที่คุณระบุ ID เฉพาะไว้ (เช่น `persist:searchbar` บนคอมโพเนนต์ใน view) เพื่อให้สามารถคงสถานะเดิมไว้ได้เมื่อมีการสลับหน้าเอกสารใหม่

นอกจากนี้ ยังมีการเปลี่ยนแปลงเชิงสถาปัตยกรรมระดับใหญ่กว่านี้อีกบางส่วนที่ [ยังอยู่ระหว่างการพิจารณาและประเมินความเป็นไปได้](https://github.com/leptos-rs/leptos/issues/1830)

## ข้อมูลเพิ่มเติม

สามารถศึกษา [ตัวอย่าง `islands`](https://github.com/leptos-rs/leptos/blob/main/examples/islands/src/app.rs), [แผนพัฒนา (roadmap)](https://github.com/leptos-rs/leptos/issues/1830) และ [เดโม Hackernews](https://github.com/leptos-rs/leptos/tree/leptos_0.6/examples/hackernews_islands_axum) เพื่อร่วมแลกเปลี่ยนความคิดเห็นและติดตามความคืบหน้าเพิ่มเติม

## โค้ดเดโม

```rust
use leptos::prelude::*;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <main style="background-color: lightblue; padding: 10px">
            <HomePage/>
        </main>
    }
}

/// Renders the home page of your application.
#[component]
fn HomePage() -> impl IntoView {
    let files = ["a.txt", "b.txt", "c.txt"];
    let labels = files.iter().copied().map(Into::into).collect();
    let tabs = move || {
        files
            .into_iter()
            .enumerate()
            .map(|(index, filename)| {
                let content = std::fs::read_to_string(filename).unwrap();
                view! {
                    <Tab index>
                        <div style="background-color: lightblue; padding: 10px">
                            <h2>{filename.to_string()}</h2>
                            <p>{content}</p>
                        </div>
                    </Tab>
                }
            })
            .collect_view()
    };

    view! {
        <h1>"Welcome to Leptos!"</h1>
        <p>"Click any of the tabs below to read a recipe."</p>
        <Tabs labels>
            <div>{tabs()}</div>
        </Tabs>
    }
}

#[island]
fn Tabs(labels: Vec<String>, children: Children) -> impl IntoView {
    let (selected, set_selected) = signal(0);
    provide_context(selected);

    let buttons = labels
        .into_iter()
        .enumerate()
        .map(|(index, label)| {
            view! {
                <button on:click=move |_| set_selected.set(index)>
                    {label}
                </button>
            }
        })
        .collect_view();
    view! {
        <div
            style="display: flex; width: 100%; justify-content: space-around;\
            background-color: lightgreen; padding: 10px;"
        >
            {buttons}
        </div>
        {children()}
    }
}

#[island]
fn Tab(index: usize, children: Children) -> impl IntoView {
    let selected = expect_context::<ReadSignal<usize>>();
    view! {
        <div
            style:background-color="lightgreen"
            style:padding="10px"
            style:display=move || if selected.get() == index {
                "block"
            } else {
                "none"
            }
        >
            {children()}
        </div>
    }
}
```
