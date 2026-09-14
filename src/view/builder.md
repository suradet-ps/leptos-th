# ไม่ใช้มาโคร: ไวยากรณ์ View Builder

> ถ้าคุณพอใจกับการใช้งานมาโคร `view!` ตามที่ได้อธิบายไว้แล้วเป็นอย่างดี คุณสามารถข้ามบทนี้ไปได้เลย ไวยากรณ์แบบ builder ที่จะอธิบายในบทนี้มีไว้เป็นทางเลือกเสริมเสมอ แต่ไม่มีความจำเป็นต้องใช้

ด้วยเหตุผลหลายประการ นักพัฒนาบางกลุ่มอาจเลือกที่จะหลีกเลี่ยงการใช้มาโคร บางทีคุณอาจไม่ชอบที่ `rustfmt` ยังรองรับมาโครได้จำกัด (แต่จริง ๆ แล้วคุณควรลองใช้ [`leptosfmt`](https://github.com/bram209/leptosfmt) ดู เพราะเป็นเครื่องมือที่ยอดเยี่ยมมาก!) หรือคุณอาจกังวลเรื่องผลกระทบต่อเวลาที่ใช้ในการคอมไพล์ หรือคุณอาจชอบความประณีตสวยงามของไวยากรณ์ภาษา Rust แท้ ๆ มากกว่า หรืออาจรู้สึกสะดุดกับการต้องสลับบริบท (context switching) ไปมาระหว่างไวยากรณ์คล้าย HTML กับโค้ด Rust ปกติ หรือคุณอาจต้องการความยืดหยุ่นในการสร้างและจัดการเอลิเมนต์ HTML ในระดับที่ลึกกว่าที่มาโคร `view` มอบให้

หากคุณอยู่ในกลุ่มใดกลุ่มหนึ่งข้างต้นนี้ ไวยากรณ์แบบ builder ก็อาจเป็นคำตอบที่เหมาะกับคุณ

มาโคร `view!` ทำหน้าที่ขยาย (expand) ไวยากรณ์คล้าย HTML ให้กลายเป็นชุดคำสั่งเรียกฟังก์ชันและเมธอดต่าง ๆ ในภาษา Rust ดังนั้น หากคุณไม่ต้องการพึ่งพามาโคร `view!` คุณก็สามารถเขียนไวยากรณ์โค้ดที่ขยายแล้วเหล่านั้นด้วยตนเองได้โดยตรง ซึ่งบอกได้เลยว่ามันทำงานได้ยอดเยี่ยมไม่แพ้กัน!

อย่างแรก หากคุณต้องการ คุณสามารถตัดมาโคร `#[component]` ทิ้งไปได้เลย เพราะแท้จริงแล้วคอมโพเนนต์ก็เป็นเพียงฟังก์ชันเริ่มต้นที่ใช้สร้างวิวของคุณเท่านั้น คุณจึงสามารถนิยามคอมโพเนนต์ขึ้นมาเป็นฟังก์ชันธรรมดาได้เลย:

```rust
pub fn counter(initial_value: i32, step: u32) -> impl IntoView { }
```

เอลิเมนต์ต่าง ๆ สามารถสร้างขึ้นได้ด้วยการเรียกฟังก์ชันที่มีชื่อเดียวกับแท็ก HTML:

```rust
p()
```

สำหรับคัสตอมเอลิเมนต์ (Custom elements) หรือ Web Components คุณสามารถสร้างได้ด้วยฟังก์ชัน [`custom()`](https://docs.rs/leptos/latest/leptos/html/fn.custom.html) โดยส่งชื่อแท็กเข้าไป:
```rust
custom("my-custom-element")
```

คุณสามารถเพิ่มคอมโพเนนต์ลูก (children) ให้กับเอลิเมนต์ได้ผ่านเมธอด [`.child()`](https://docs.rs/leptos/latest/leptos/html/trait.ElementChild.html#tymethod.child) ซึ่งรับได้ทั้ง child เดี่ยว ๆ หรือ tuple/array ของชนิดข้อมูลที่อิมพลีเมนต์ [`IntoView`](https://docs.rs/leptos/latest/leptos/trait.IntoView.html):

```rust
p().child((em().child("Big, "), strong().child("bold "), "text"))
```

คุณสามารถกำหนดแอตทริบิวต์ได้ด้วย [`.attr()`](https://docs.rs/leptos/latest/leptos/attr/custom/trait.CustomAttribute.html#method.attr) ซึ่งรองรับชนิดข้อมูลแบบเดียวกับที่คุณส่งให้กับแอตทริบิวต์ในมาโคร view (กล่าวคือ ชนิดข้อมูลใดก็ตามที่อิมพลีเมนต์ [`Attribute`](https://docs.rs/leptos/latest/leptos/attr/trait.Attribute.html)):

```rust
p().attr("id", "foo")
    .attr("data-count", move || count.get().to_string())
```

นอกจากนี้ ยังสามารถกำหนดผ่านเมธอดเฉพาะของแอตทริบิวต์ ซึ่งมีเตรียมไว้ให้สำหรับชื่อแอตทริบิวต์มาตรฐานของ HTML ทุกตัว:

```rust
p().id("foo")
    .attr("data-count", move || count.get().to_string())
```

ในทำนองเดียวกัน ไวยากรณ์ `class:`, `prop:` และ `style:` ก็จะแมปตรงกับเมธอด [`.class()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.ClassAttribute.html#tymethod.class), [`.prop()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.PropAttribute.html#tymethod.prop) และ [`.style()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.StyleAttribute.html#tymethod.style) ตามลำดับ

คุณสามารถผูกตัวรับฟังเหตุการณ์ (event listeners) ได้ด้วยเมธอด [`.on()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.OnAttribute.html#tymethod.on) โดยชนิดข้อมูลอีเวนต์ที่มีการระบุ type ชัดเจนในโมดูล [`leptos::ev`](https://docs.rs/leptos/latest/leptos/tachys/html/event/index.html) จะช่วยป้องกันข้อผิดพลาดจากการพิมพ์ชื่ออีเวนต์ผิด และช่วยให้คอมไพเลอร์อนุมานชนิดข้อมูลในฟังก์ชันคอลแบ็กได้อย่างแม่นยำ

```rust
button()
    .on(ev::click, move |_| set_count.set(0))
    .child("Clear")
```

ทั้งหมดนี้รวมกันเป็นไวยากรณ์ภาษา Rust แท้ ๆ ที่ช่วยให้คุณสร้างวิวที่สมบูรณ์แบบได้ หากคุณชื่นชอบการเขียนในสไตล์นี้:

```rust
/// A simple counter view.
// A component is really just a function call: it runs once to create the DOM and reactive system
pub fn counter(initial_value: i32, step: i32) -> impl IntoView {
    let (count, set_count) = signal(initial_value);
    div().child((
        button()
            // typed events found in leptos::ev
            // 1) prevent typos in event names
            // 2) allow for correct type inference in callbacks
            .on(ev::click, move |_| set_count.set(0))
            .child("Clear"),
        button()
            .on(ev::click, move |_| *set_count.write() -= step)
            .child("-1"),
        span().child(("Value: ", move || count.get(), "!")),
        button()
            .on(ev::click, move |_| *set_count.write() += step)
            .child("+1"),
    ))
}
```

## การใช้คอมโพเนนต์กับไวยากรณ์แบบ builder

สำหรับการสร้างคอมโพเนนต์ของคุณเองด้วยไวยากรณ์แบบ builder คุณสามารถใช้ฟังก์ชันธรรมดาได้เลย (ดังตัวอย่างด้านบน) ส่วนการนำคอมโพเนนต์อื่น ๆ มาใช้งาน (เช่น คอมโพเนนต์จัดการโฟลว์ในตัวอย่าง `For` หรือ `Show`) คุณสามารถใช้ประโยชน์จากข้อเท็จจริงที่ว่า คอมโพเนนต์แต่ละตัวคือฟังก์ชันที่รับอาร์กิวเมนต์เป็นสตรัคต์พร็อพเพียงตัวเดียว และสตรัคต์พร็อพเหล่านั้นก็มี builder ของตัวเองเตรียมไว้ให้อยู่แล้ว

คุณสามารถเลือกใช้ builder ของพร็อพคอมโพเนนต์ได้ดังนี้:
```rust
use leptos::html::p;

let (value, set_value) = signal(0);

Show(
    ShowProps::builder()
        .when(move || value.get() > 5)
        .fallback(|| p().child("I will appear if `value` is 5 or lower"))
        .children(ToChildren::to_children(|| {
            p().child("I will appear if `value` is above 5")
        }))
        .build(),
)
```
หรือจะสร้างอินสแตนซ์ของสตรัคต์พร็อพขึ้นมาโดยตรงเลยก็ได้:
```rust
use leptos::html::p;

let (value, set_value) = signal(0);

Show(ShowProps {
    when: move || value.get() > 5,
    fallback: (|| p().child("I will appear if `value` is 5 or lower")).into(),
    children: ToChildren::to_children(|| p().child("I will appear if `value` is above 5")),
})
```
การใช้ builder ของคอมโพเนนต์จะช่วยจัดการตัวแปลงชนิดข้อมูลอย่าง `#[prop(into)]` ให้โดยอัตโนมัติ ส่วนการส่งสตรัคต์โดยตรง เราจะต้องแปลงค่าด้วยตนเอง เช่น การเรียกใช้ `.into()` อย่างที่เห็นในโค้ด

## การขยายมาโคร

แน่นอนว่าเราไม่ได้นำฟีเจอร์ทั้งหมดของมาโคร `view!` หรือ `#[component]` มาแจกแจงอย่างละเอียดไว้ที่นี่ อย่างไรก็ตาม ภาษา Rust มีเครื่องมือทรงพลังที่จะช่วยให้คุณเข้าใจสิ่งที่เกิดขึ้นเบื้องหลังมาโครได้อย่างทะลุปรุโปร่ง โดยเฉพาะ[ฟีเจอร์ “expand macro recursively” ของ rust-analyzer](https://rust-analyzer.github.io/book/features.html#expand-macro-recursively) ซึ่งช่วยให้คุณสั่งคลี่มาโครตัวใดก็ได้ออกมาดูโค้ดจริงที่ถูกสร้างขึ้น รวมถึงเครื่องมืออย่าง [`cargo-expand`](https://crates.io/crates/cargo-expand) ที่สามารถขยายมาโครทั้งหมดในโปรเจกต์ออกมาเป็นโค้ด Rust ปกติได้ สำหรับเนื้อหาส่วนที่เหลือในหนังสือเล่มนี้ เราจะยังคงใช้ไวยากรณ์มาโคร `view!` เป็นหลัก แต่หากคุณต้องการทราบว่าโค้ดเหล่านั้นจะเขียนในรูปแบบของ builder ได้อย่างไร คุณก็สามารถใช้เครื่องมือเหล่านี้เข้ามาช่วยสำรวจดูโค้ดเบื้องหลังได้เสมอ
