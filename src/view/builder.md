# ไม่ใช้มาโคร: ไวยากรณ์ View Builder

> ถ้าคุณพอใจกับไวยากรณ์มาโคร `view!` ที่อธิบายมาแล้วเป็นอย่างดี คุณยินดีข้ามบทนี้ไปได้เลย ไวยากรณ์แบบ builder ที่อธิบายในส่วนนี้มีให้ใช้เสมอ แต่ไม่เคยจำเป็นต้องใช้

ด้วยเหตุผลใดเหตุผลหนึ่ง นักพัฒนาหลายคนมักเลือกที่จะเลี่ยงมาโคร บางทีคุณอาจไม่ชอบการรองรับ `rustfmt` ที่จำกัด (ถึงอย่างนั้น คุณควรลองใช้ [`leptosfmt`](https://github.com/bram209/leptosfmt) ดู ซึ่งเป็นเครื่องมือที่ยอดเยี่ยม!) บางทีคุณอาจกังวลเกี่ยวกับผลกระทบของมาโครที่มีต่อเวลาคอมไพล์ บางทีคุณอาจชอบความสวยงามของไวยากรณ์ Rust แท้ๆ หรือคุณอาจมีปัญหาในการสลับบริบทไปมาระหว่างไวยากรณ์คล้าย HTML กับโค้ด Rust ของคุณ หรือบางทีคุณอาจต้องการความยืดหยุ่นในการสร้างและจัดการเอลิเมนต์ HTML มากกว่าที่มาโคร `view` มอบให้

ถ้าคุณอยู่ในกลุ่มใดกลุ่มหนึ่งเหล่านี้ ไวยากรณ์แบบ builder อาจเหมาะกับคุณ

มาโคร `view` ขยายไวยากรณ์คล้าย HTML ให้เป็นชุดของฟังก์ชัน Rust และการเรียกเมธอด ถ้าคุณไม่อยากใช้มาโคร `view` คุณก็ใช้ไวยากรณ์ที่ขยายแล้วนั้นด้วยตัวเองได้เลย และจริงๆ แล้วมันก็ดีใช้ได้เลย!

อย่างแรก ถ้าคุณต้องการ คุณทิ้งมาโคร `#[component]` ไปเลยก็ได้: คอมโพเนนต์ก็เป็นแค่ฟังก์ชันตั้งต้นที่สร้างวิวของคุณ คุณจึงนิยามคอมโพเนนต์เป็นฟังก์ชันง่ายๆ ได้:

```rust
pub fn counter(initial_value: i32, step: u32) -> impl IntoView { }
```

เอลิเมนต์ถูกสร้างขึ้นโดยเรียกฟังก์ชันที่มีชื่อเดียวกับเอลิเมนต์ HTML:

```rust
p()
```

เอลิเมนต์แบบกำหนดเอง/เว็บคอมโพเนนต์สามารถสร้างได้โดยใช้ฟังก์ชัน [`custom()`](https://docs.rs/leptos/latest/leptos/html/fn.custom.html) พร้อมกับชื่อของมัน:
```rust
custom("my-custom-element")
```

คุณเพิ่มลูก (children) ให้กับเอลิเมนต์ได้ด้วย [`.child()`](https://docs.rs/leptos/latest/leptos/html/trait.ElementChild.html#tymethod.child) ซึ่งรับ child หนึ่งตัว หรือทูเพิลหรืออาร์เรย์ของชนิดข้อมูลที่อิมพลีเมนต์ [`IntoView`](https://docs.rs/leptos/latest/leptos/trait.IntoView.html)

```rust
p().child((em().child("Big, "), strong().child("bold "), "text"))
```

แอตทริบิวต์ถูกเพิ่มด้วย [`.attr()`](https://docs.rs/leptos/latest/leptos/attr/custom/trait.CustomAttribute.html#method.attr) ซึ่งรับชนิดข้อมูลใดก็ได้เหมือนกับที่คุณส่งเป็นแอตทริบิวต์เข้าไปในมาโคร view ได้ (ชนิดข้อมูลที่อิมพลีเมนต์ [`Attribute`](https://docs.rs/leptos/latest/leptos/attr/trait.Attribute.html))

```rust
p().attr("id", "foo")
    .attr("data-count", move || count.get().to_string())
```

นอกจากนี้ยังเพิ่มได้ด้วยเมธอดแอตทริบิวต์ ซึ่งมีให้ใช้สำหรับชื่อแอตทริบิวต์ HTML ที่มีมาให้ทุกตัว:

```rust
p().id("foo")
    .attr("data-count", move || count.get().to_string())
```

ในทำนองเดียวกัน ไวยากรณ์ `class:` `prop:` และ `style:` ก็แมปโดยตรงเข้ากับเมธอด [`.class()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.ClassAttribute.html#tymethod.class) [`.prop()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.PropAttribute.html#tymethod.prop) และ [`.style()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.StyleAttribute.html#tymethod.style)

ตัวรับฟังเหตุการณ์ถูกเพิ่มได้ด้วย [`.on()`](https://docs.rs/leptos/latest/leptos/attr/global/trait.OnAttribute.html#tymethod.on) อีเวนต์แบบมีชนิดที่พบใน [`leptos::ev`](https://docs.rs/leptos/latest/leptos/tachys/html/event/index.html) ช่วยป้องกันการพิมพ์ชื่ออีเวนต์ผิดพลาดและช่วยให้อนุมานชนิดข้อมูลในฟังก์ชันคอลแบ็กได้อย่างถูกต้อง

```rust
button()
    .on(ev::click, move |_| set_count.set(0))
    .child("Clear")
```

ทั้งหมดนี้รวมกันเป็นไวยากรณ์แบบ Rust แท้ๆ สำหรับสร้างวิวที่ครบครัน หากคุณชอบสไตล์นี้

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

การสร้างคอมโพเนนต์ของคุณเองด้วยไวยากรณ์แบบ builder คุณใช้ฟังก์ชันธรรมดาได้เลย (ดูด้านบน) ส่วนการใช้งานคอมโพเนนต์อื่นๆ (ตัวอย่างเช่น คอมโพเนนต์ควบคุมโฟลว์ `For` หรือ `Show` ที่มีมาให้) คุณใช้ประโยชน์จากข้อเท็จจริงที่ว่าแต่ละคอมโพเนนต์เป็นฟังก์ชันที่รับอาร์กิวเมนต์พร็อพของคอมโพเนนต์หนึ่งตัว และพร็อพของคอมโพเนนต์มี builder ของตัวเอง

คุณจะใช้ builder ของพร็อพคอมโพเนนต์ก็ได้:
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
หรือจะสร้างสตรัคต์พร็อพโดยตรงก็ได้:
```rust
use leptos::html::p;

let (value, set_value) = signal(0);

Show(ShowProps {
    when: move || value.get() > 5,
    fallback: (|| p().child("I will appear if `value` is 5 or lower")).into(),
    children: ToChildren::to_children(|| p().child("I will appear if `value` is above 5")),
})
```
การใช้ builder ของคอมโพเนนต์จะใช้ตัวปรับแต่งต่างๆ เช่น `#[prop(into)]` ให้อย่างถูกต้อง ส่วนการใช้ไวยากรณ์แบบสตรัคต์ เราได้ใช้มันด้วยตัวเองโดยเรียก `.into()` เอง

## การขยายมาโคร

ไม่ใช่ทุกฟีเจอร์ของไวยากรณ์มาโคร `view` หรือ `component` ที่ถูกอธิบายไว้อย่างละเอียดตรงนี้ อย่างไรก็ตาม Rust มีเครื่องมือที่คุณต้องใช้เพื่อทำความเข้าใจว่าเกิดอะไรขึ้นกับมาโครใดๆ โดยเฉพาะ[ฟีเจอร์ “expand macro recursively” ของ rust-analyzer](https://rust-analyzer.github.io/book/features.html#expand-macro-recursively) ที่ให้คุณขยายมาโครใดก็ได้เพื่อดูโค้ดที่มันสร้างขึ้น และ [`cargo-expand`](https://crates.io/crates/cargo-expand) จะขยายมาโครทั้งหมดในโปรเจกต์ให้เป็นโค้ด Rust ปกติ ส่วนที่เหลือของหนังสือเล่มนี้จะยังใช้ไวยากรณ์มาโคร `view` ต่อไป แต่ถ้าคุณไม่แน่ใจว่าจะแปลงมันเป็นไวยากรณ์แบบ builder อย่างไร คุณก็ใช้เครื่องมือเหล่านี้สำรวจโค้ดที่ถูกสร้างขึ้นได้
