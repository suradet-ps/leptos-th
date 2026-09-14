# การควบคุมโฟลว์

ในแอปพลิเคชันส่วนใหญ่ ย่อมต้องมีจังหวะที่เราต้องตัดสินใจ เช่น: ควรแสดงผลส่วนนี้ของวิวหรือไม่? ควรแสดง `<ButtonA/>` หรือ `<WidgetB/>` ดี? ตรรกะแบบมีเงื่อนไขเหล่านี้คือสิ่งที่เราเรียกว่า **การควบคุมโฟลว์ (Control Flow)**

## เคล็ดลับเล็กน้อย

เมื่อคิดว่าจะจัดการเรื่องนี้ใน Leptos อย่างไร มีหลักการสำคัญที่ควรระลึกไว้ดังนี้:

1. Rust เป็นภาษาที่เน้นนิพจน์ (expression-oriented): คำสั่งควบคุมโฟลว์อย่าง `if x() { y } else { z }` และ `match x() { ... }` ล้วนเป็นนิพจน์ที่คืนค่าผลลัพธ์ออกมาได้เสมอ ซึ่งมีประโยชน์อย่างยิ่งในการเขียน UI เชิงประกาศ (declarative UI)
2. สำหรับชนิดข้อมูล `T` ใด ๆ ที่อิมพลีเมนต์ `IntoView` (กล่าวคือ ชนิดข้อมูลใดก็ตามที่ Leptos รู้วิธีเรนเดอร์) ตัว `Option<T>` และ `Result<T, impl Error>` *ก็* อิมพลีเมนต์ `IntoView` ด้วยเช่นกัน และในทำนองเดียวกับที่ `Fn() -> T` สามารถเรนเดอร์ `T` แบบรีแอกทีฟได้ ทั้ง `Fn() -> Option<T>` และ `Fn() -> Result<T, impl Error>` ก็เป็นรีแอกทีฟเช่นเดียวกัน
3. Rust มีเมธอดตัวช่วยที่ทรงพลังมากมาย เช่น [Option::map](https://doc.rust-lang.org/std/option/enum.Option.html#method.map), [Option::and_then](https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then), [Option::ok_or](https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or), [Result::map](https://doc.rust-lang.org/std/result/enum.Result.html#method.map), [Result::ok](https://doc.rust-lang.org/std/result/enum.Result.html#method.ok) และ [bool::then](https://doc.rust-lang.org/std/primitive.bool.html#method.then) ซึ่งช่วยให้คุณแปลงชนิดข้อมูลมาตรฐานต่าง ๆ ไปมาในเชิงประกาศได้อย่างคล่องตัว และผลลัพธ์เหล่านั้นนำไปเรนเดอร์ได้ทันที การศึกษาเอกสารของ `Option` และ `Result` ให้เชี่ยวชาญจึงเป็นหนึ่งในวิธีที่ยอดเยี่ยมที่สุดในการยกระดับทักษะภาษา Rust ของคุณ
4. อย่าลืมกฎทองที่ว่า: การที่ค่าใด ๆ จะตอบสนองแบบรีแอกทีฟได้ ค่านั้นจะต้องอยู่ในรูปของฟังก์ชัน คุณจึงจะเห็นเราห่อโค้ดต่าง ๆ ด้วยโคลเชอร์ `move ||` อยู่บ่อยครั้งด้านล่างนี้ เพื่อให้แน่ใจว่าโค้ดจะถูกประมวลผลซ้ำเมื่อสัญญาณที่มันพึ่งพาเกิดการเปลี่ยนแปลง และทำให้ UI ปรับตามได้อย่างทันท่วงที

## แล้วสิ่งนี้หมายความว่าอะไร?

เมื่อนำเรื่องเหล่านี้มาประกอบเข้าด้วยกัน นั่นหมายความว่าคุณสามารถจัดการการควบคุมโฟลว์ส่วนใหญ่ได้ด้วยไวยากรณ์มาตรฐานของ Rust ล้วน ๆ โดยแทบไม่ต้องพึ่งพาคอมโพเนนต์ควบคุมโฟลว์พิเศษหรือเวทมนตร์ใด ๆ เลย

ตัวอย่างเช่น เริ่มจากสัญญาณง่าย ๆ และสัญญาณอนุพัทธ์:

```rust
let (value, set_value) = signal(0);
let is_odd = move || value.get() % 2 != 0;
```

เราใช้สัญญาณเหล่านี้ร่วมกับคำสั่ง Rust ธรรมดาเพื่อสร้างการควบคุมโฟลว์ได้เกือบทั้งหมด

### คำสั่ง `if`

สมมติว่าเราต้องการเรนเดอร์ข้อความหนึ่งถ้าตัวเลขเป็นเลขคี่ และแสดงอีกข้อความหนึ่งถ้าเป็นเลขคู่ เราสามารถเขียนตรง ๆ ได้แบบนี้:

```rust
view! {
    <p>
        {move || if is_odd() {
            "Odd"
        } else {
            "Even"
        }}
    </p>
}
```

นิพจน์ `if` จะคืนค่าผลลัพธ์ออกมา และ `&str` ก็อิมพลีเมนต์ `IntoView` อยู่แล้ว ทำให้ `Fn() -> &str` อิมพลีเมนต์ `IntoView` ไปด้วยโดยปริยาย โค้ดชุดนี้จึงทำงานได้ทันทีอย่างเป็นธรรมชาติ!

### `Option<T>`

สมมติว่าเราต้องการแสดงข้อความเมื่อเป็นเลขคี่ และไม่แสดงอะไรเลยเมื่อเป็นเลขคู่:

```rust
let message = move || {
    if is_odd() {
        Some("Ding ding ding!")
    } else {
        None
    }
};

view! {
    <p>{message}</p>
}
```

โค้ดนี้ทำงานได้เป็นอย่างดี และเรายังสามารถเขียนให้กระชับยิ่งขึ้นได้ด้วยการใช้ `bool::then()`:

```rust
let message = move || is_odd().then(|| "Ding ding ding!");
view! {
    <p>{message}</p>
}
```

คุณสามารถเขียนนิพจน์นี้แบบอินไลน์ลงในมาโคร `view!` ได้เลยตามใจชอบ แม้ว่าในบางครั้งการแยกออกมาเขียนเป็นตัวแปรภายนอก `view!` จะช่วยให้ `cargo fmt` และ `rust-analyzer` จัดรูปแบบและแนะนำโค้ดได้สะดวกกว่าก็ตาม

### คำสั่ง `match`

ในเมื่อเรากำลังเขียนโค้ด Rust ปกติ คุณจึงสามารถใช้พลังทั้งหมดของ pattern matching ใน Rust ได้อย่างเต็มที่:

```rust
let message = move || {
    match value.get() {
        0 => "Zero",
        1 => "One",
        n if is_odd() => "Odd",
        _ => "Even"
    }
};
view! {
    <p>{message}</p>
}
```

เห็นไหมครับว่าไม่มีอะไรซับซ้อนเลย ทุกอย่างเป็นไปตามธรรมชาติของ Rust!

## การป้องกันการเรนเดอร์เกินความจำเป็น

แต่ช้าก่อน... มันอาจไม่ได้เรียบง่ายขนาดนั้นเสมอไป

แม้ทุกตัวอย่างที่เราเพิ่งเขียนไปจะทำงานได้ถูกต้องตามตรรกะ แต่มีจุดสำคัญอย่างหนึ่งที่คุณต้องพึงระวัง: ฟังก์ชันควบคุมโฟลว์ทั้งหมดที่เราสร้างขึ้นมานั้นทำงานในฐานะสัญญาณอนุพัทธ์ (derived signal) ซึ่งหมายความว่ามันจะถูกรันซ้ำทุกครั้งที่สัญญาณต้นทางเปลี่ยนค่า ในตัวอย่างข้างต้นที่ค่าสลับระหว่างคู่กับคี่ทุกครั้ง การรันใหม่ทุกรอบก็ถือว่าสมเหตุสมผลดี

แต่ลองพิจารณาตัวอย่างต่อไปนี้:

```rust
let (value, set_value) = signal(0);

let message = move || if value.get() > 5 {
    "Big"
} else {
    "Small"
};

view! {
    <p>{message}</p>
}
```

โค้ดนี้ *ทำงานได้* แน่นอน แต่ถ้าคุณลองใส่ล็อกเข้าไป คุณอาจต้องแปลกใจ:

```rust
let message = move || if value.get() > 5 {
    logging::log!("{}: rendering Big", value.get());
    "Big"
} else {
    logging::log!("{}: rendering Small", value.get());
    "Small"
};
```

เมื่อผู้ใช้คลิกปุ่มเพิ่มค่า `value` ไปเรื่อย ๆ คุณจะเห็นข้อความในล็อกปรากฏดังนี้:

```
1: rendering Small
2: rendering Small
3: rendering Small
4: rendering Small
5: rendering Small
6: rendering Big
7: rendering Big
8: rendering Big
... ad infinitum
```

ทุกครั้งที่ `value` เปลี่ยน เงื่อนไข `if` จะถูกประเมินใหม่เสมอ ซึ่งตรงตามกลไกของระบบรีแอกทิวิตี แต่มันมีข้อเสียที่ต้องคำนึงถึง: สำหรับโหนดข้อความสั้น ๆ การประเมินซ้ำและอัปเดตข้อความใหม่อาจไม่ใช่เรื่องใหญ่ แต่ลองจินตนาการดูว่าหากเป็นคอมโพเนนต์แบบนี้:

```rust
let message = move || if value.get() > 5 {
    <Big/>
} else {
    <Small/>
};
```

โค้ดนี้จะเรนเดอร์ `<Small/>` ขึ้นมาใหม่ซ้ำ ๆ ถึง 5 ครั้ง และเมื่อค่าเกิน 5 ก็จะเรนเดอร์ `<Big/>` ขึ้นมาใหม่ซ้ำ ๆ ทุกรอบการคลิก! หากคอมโพเนนต์เหล่านั้นต้องโหลดข้อมูล สร้างสัญญาณ หรือสร้างโหนด DOM ที่ซับซ้อน การทำลายแล้วสร้างใหม่ซ้ำ ๆ เช่นนี้ย่อมเป็นการสิ้นเปลืองทรัพยากรโดยใช่เหตุ

### `<Show/>`

คอมโพเนนต์ [`<Show/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.Show.html) คือทางออกสำหรับเรื่องนี้ คุณเพียงส่งฟังก์ชันเงื่อนไขให้กับพร็อพ `when`, ส่งวิวสำรองให้กับ `fallback` (ที่จะแสดงผลเมื่อ `when` คืนค่า `false`) และส่งลูก (children) ที่ต้องการเรนเดอร์เมื่อ `when` เป็น `true`

```rust
let (value, set_value) = signal(0);

view! {
  <Show
    when=move || { value.get() > 5 }
    fallback=|| view! { <Small/> }
  >
    <Big/>
  </Show>
}
```

`<Show/>` จะทำการเมโมไมซ์เงื่อนไข `when` ไว้ ทำให้มันเรนเดอร์ `<Small/>` เพียงครั้งเดียว และแสดงคอมโพเนนต์เดิมต่อไปเรื่อย ๆ จนกว่า `value` จะมากกว่า 5 จากนั้นจึงเรนเดอร์ `<Big/>` เพียงครั้งเดียว และคงอยู่ต่อไปจนกว่า `value` จะลดลงต่ำกว่า 5 อีกครั้ง

นี่จึงเป็นเครื่องมือที่มีประโยชน์อย่างยิ่งในการหลีกเลี่ยงการเรนเดอร์ซ้ำซ้อนเมื่อใช้นิพจน์ `if` แบบไดนามิก อย่างไรก็ตาม คอมโพเนนต์นี้ก็มี overhead เล็กน้อย ดังนั้นสำหรับโหนดง่าย ๆ (เช่น การอัปเดตโหนดข้อความธรรมดา หรือสลับแอตทริบิวต์) การใช้ `move || if ...` จะมีประสิทธิภาพสูงกว่า แต่หากการเรนเดอร์สาขาใดสาขาหนึ่งมีค่าใช้จ่ายสูง การเลือกใช้ `<Show/>` ย่อมเหมาะสมกว่าเสมอ

## หมายเหตุ: การแปลงชนิดข้อมูล

ยังมีอีกเรื่องสุดท้ายที่สำคัญต้องกล่าวถึงในหัวข้อนี้

Leptos ใช้โครงสร้างวิวทรีแบบระบุชนิดข้อมูลตอนคอมไพล์ (statically-typed view tree) โดยมาโคร `view` จะคืนค่าชนิดข้อมูลที่แตกต่างกันสำหรับวิวแต่ละรูปแบบ

โค้ดต่อไปนี้จะคอมไพล์ไม่ผ่าน เพราะเอลิเมนต์ HTML ที่ต่างกันจะมีชนิดข้อมูลใน Rust ไม่เหมือนกัน:

```rust,compile_error
view! {
    <main>
        {move || match is_odd() {
            true if value.get() == 1 => {
                view! { <pre>"One"</pre> }
            },
            false if value.get() == 2 => {
                view! { <p>"Two"</p> }
            }
            // returns HtmlElement<Textarea>
            _ => view! { <textarea>{value.get()}</textarea> }
        }}
    </main>
}
```

ระบบ type ที่เข้มงวดนี้ทรงพลังมาก เพราะเปิดทางให้คอมไพเลอร์ช่วยปรับแต่งประสิทธิภาพได้อย่างมหาศาล แต่สำหรับตรรกะแบบมีเงื่อนไขเช่นนี้อาจทำให้ติดขัดได้ เพราะในภาษา Rust คุณไม่สามารถคืนค่าชนิดข้อมูลที่แตกต่างกันจากแต่ละสาขาของ `match` หรือ `if` ได้ ทางออกสำหรับสถานการณ์นี้มีอยู่ 2 วิธีด้วยกัน:

1. ใช้ enum `Either` (และ `EitherOf3`, `EitherOf4` ฯลฯ) เพื่อรวมชนิดข้อมูลที่แตกต่างกันให้อยู่ในชนิด enum เดียวกัน
2. ใช้ `.into_any()` เพื่อแปลงวิวหลากชนิดให้กลายเป็น `AnyView` ที่ลบข้อมูลชนิดออก (type-erased) ตัวเดียว

นี่คือตัวอย่างเดิม แต่เพิ่มการแปลงชนิดข้อมูลเข้าไปเรียบร้อยแล้ว:

```rust,compile_error
view! {
    <main>
        {move || match is_odd() {
            true if value.get() == 1 => {
                // returns HtmlElement<Pre>
                view! { <pre>"One"</pre> }.into_any()
            },
            false if value.get() == 2 => {
                // returns HtmlElement<P>
                view! { <p>"Two"</p> }.into_any()
            }
            // returns HtmlElement<Textarea>
            _ => view! { <textarea>{value.get()}</textarea> }.into_any()
        }}
    </main>
}
```

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/6-control-flow-0-7-3m4c9j?file=%2Fsrc%2Fmain.rs%3A1%2C1-91%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/6-control-flow-0-7-3m4c9j?file=%2Fsrc%2Fmain.rs%3A1%2C1-91%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (value, set_value) = signal(0);
    let is_odd = move || value.get() & 1 == 1;
    let odd_text = move || if is_odd() {
        Some("How odd!")
    } else {
        None
    };

    view! {
        <h1>"Control Flow"</h1>

        // Simple UI to update and show a value
        <button on:click=move |_| *set_value.write() += 1>
            "+1"
        </button>
        <p>"Value is: " {value}</p>

        <hr/>

        <h2><code>"Option<T>"</code></h2>
        // For any `T` that implements `IntoView`,
        // so does `Option<T>`

        <p>{odd_text}</p>
        // This means you can use `Option` methods on it
        <p>{move || odd_text().map(|text| text.len())}</p>

        <h2>"Conditional Logic"</h2>
        // You can do dynamic conditional if-then-else
        // logic in several ways
        //
        // a. An "if" expression in a function
        //    This will simply re-render every time the value
        //    changes, which makes it good for lightweight UI
        <p>
            {move || if is_odd() {
                "Odd"
            } else {
                "Even"
            }}
        </p>

        // b. Toggling some kind of class
        //    This is smart for an element that's going to
        //    toggled often, because it doesn't destroy
        //    it in between states
        //    (you can find the `hidden` class in `index.html`)
        <p class:hidden=is_odd>"Appears if even."</p>

        // c. The <Show/> component
        //    This only renders the fallback and the child
        //    once, lazily, and toggles between them when
        //    needed. This makes it more efficient in many cases
        //    than a {move || if ...} block
        <Show when=is_odd
            fallback=|| view! { <p>"Even steven"</p> }
        >
            <p>"Oddment"</p>
        </Show>

        // d. Because `bool::then()` converts a `bool` to
        //    `Option`, you can use it to create a show/hide toggled
        {move || is_odd().then(|| view! { <p>"Oddity!"</p> })}

        <h2>"Converting between Types"</h2>
        // e. Note: if branches return different types,
        //    you can convert between them with
        //    `.into_any()` or using the `Either` enums
        //    (`Either`, `EitherOf3`, `EitherOf4`, etc.)
        {move || match is_odd() {
            true if value.get() == 1 => {
                // <pre> returns HtmlElement<Pre>
                view! { <pre>"One"</pre> }.into_any()
            },
            false if value.get() == 2 => {
                // <p> returns HtmlElement<P>
                // so we convert into a more generic type
                view! { <p>"Two"</p> }.into_any()
            }
            _ => view! { <textarea>{value.get()}</textarea> }.into_any()
        }}
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
