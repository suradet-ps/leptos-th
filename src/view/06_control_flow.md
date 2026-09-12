# การควบคุมโฟลว์

ในแอปพลิเคชันส่วนใหญ่ บางครั้งคุณต้องตัดสินใจว่า ควรเรนเดอร์ส่วนนี้ของวิวหรือไม่? ควรเรนเดอร์ `<ButtonA/>` หรือ `<WidgetB/>`? นี่แหละคือ **การควบคุมโฟลว์**

## เคล็ดลับเล็กน้อย

เมื่อคิดว่าจะทำสิ่งนี้กับ Leptos อย่างไร สิ่งสำคัญคือต้องจำไว้ว่า:

1. Rust เป็นภาษาที่เน้นนิพจน์ (expression-oriented) นิพจน์ควบคุมโฟลว์อย่าง `if x() { y } else { z }` และ `match x() { ... }` จะคืนค่าของตัวเองออกมา สิ่งนี้ทำให้มันมีประโยชน์มากสำหรับส่วนติดต่อผู้ใช้แบบประกาศ
2. สำหรับ `T` ใดก็ตามที่อิมพลีเมนต์ `IntoView` หรือพูดอีกอย่างคือ สำหรับชนิดข้อมูลใดก็ตามที่ Leptos รู้วิธีเรนเดอร์ `Option<T>` และ `Result<T, impl Error>` *ก็* อิมพลีเมนต์ `IntoView` เช่นกัน และเช่นเดียวกับที่ `Fn() -> T` เรนเดอร์ `T` แบบรีแอกทีฟ `Fn() -> Option<T>` และ `Fn() -> Result<T, impl Error>` ก็เป็นรีแอกทีฟด้วย
3. Rust มีตัวช่วยที่มีประโยชน์มากมายอย่าง [Option::map](https://doc.rust-lang.org/std/option/enum.Option.html#method.map), [Option::and_then](https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then), [Option::ok_or](https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or), [Result::map](https://doc.rust-lang.org/std/result/enum.Result.html#method.map), [Result::ok](https://doc.rust-lang.org/std/result/enum.Result.html#method.ok) และ [bool::then](https://doc.rust-lang.org/std/primitive.bool.html#method.then) ที่ให้คุณแปลงระหว่างชนิดข้อมูลมาตรฐานต่างๆ ได้หลายแบบในเชิงประกาศ ซึ่งทั้งหมดนั้นเรนเดอร์ได้ การใช้เวลากับเอกสารของ `Option` และ `Result` โดยเฉพาะเป็นวิธีที่ดีที่สุดวิธีหนึ่งในการยกระดับฝีมือ Rust ของคุณ
4. และขอให้จำไว้เสมอว่า การจะเป็นรีแอกทีฟได้ ค่าต่างๆ ต้องเป็นฟังก์ชัน คุณจะเห็นผมห่อสิ่งต่างๆ ด้วยโคลเชอร์ `move ||` อยู่บ่อยๆ ด้านล่างนี้ เพื่อให้แน่ใจว่ามันจะรันซ้ำจริงเมื่อสัญญาณที่มันพึ่งพาเปลี่ยนไป และรักษา UI ให้เป็นรีแอกทีฟ

## แล้วสิ่งนี้หมายความว่าอะไร?

เพื่อเชื่อมจุดต่างๆ เข้าด้วยกันสักหน่อย นี่หมายความว่าจริงๆ แล้วคุณสามารถเขียนการควบคุมโฟลว์ส่วนใหญ่ด้วยโค้ด Rust ล้วนๆ ได้ โดยไม่ต้องใช้คอมโพเนนต์ควบคุมโฟลว์หรือความรู้พิเศษใดๆ

ตัวอย่างเช่น เริ่มจากสัญญาณง่ายๆ และสัญญาณอนุพัทธ์:

```rust
let (value, set_value) = signal(0);
let is_odd = move || value.get() % 2 != 0;
```

เราใช้สัญญาณเหล่านี้กับ Rust ธรรมดาเพื่อสร้างการควบคุมโฟลว์ส่วนใหญ่ได้

### คำสั่ง `if`

สมมติว่าผมต้องการเรนเดอร์ข้อความบางอย่างถ้าตัวเลขเป็นเลขคี่ และข้อความอื่นถ้าเป็นเลขคู่ ถ้างั้นลองแบบนี้เป็นไง?

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

นิพจน์ `if` คืนค่าของตัวเอง และ `&str` อิมพลีเมนต์ `IntoView` ดังนั้น `Fn() -> &str` ก็อิมพลีเมนต์ `IntoView` ฉะนั้นสิ่งนี้... ก็แค่ทำงานได้เลย!

### `Option<T>`

สมมติว่าเราต้องการเรนเดอร์ข้อความถ้าเป็นเลขคี่ และไม่เรนเดอร์อะไรถ้าเป็นเลขคู่

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

แบบนี้ก็ใช้ได้ดี เราทำให้สั้นลงอีกนิดได้ถ้าต้องการ โดยใช้ `bool::then()`

```rust
let message = move || is_odd().then(|| "Ding ding ding!");
view! {
    <p>{message}</p>
}
```

คุณจะเขียนมันแบบอินไลน์ตรงนี้เลยก็ได้ถ้าต้องการ ถึงแม้ว่าส่วนตัวผมบางครั้งจะชอบการสนับสนุน `cargo fmt` และ `rust-analyzer` ที่ดีกว่าซึ่งได้มาจากการดึงสิ่งเหล่านี้ออกจาก `view` ก็ตาม

### คำสั่ง `match`

เรายังคงเขียนโค้ด Rust ธรรมดาอยู่ใช่ไหม? ดังนั้นคุณจึงมีพลังทั้งหมดของการจับคู่แพตเทิร์นของ Rust ให้ใช้ได้เต็มที่

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

แล้วทำไมจะไม่ได้ล่ะ? YOLO ใช่ไหมล่ะ?

## การป้องกันการเรนเดอร์เกินความจำเป็น

ไม่ YOLO ขนาดนั้นหรอก

ทุกอย่างที่เราเพิ่งทำไปนั้นโดยพื้นฐานก็ใช้ได้หมด แต่มีสิ่งหนึ่งที่คุณควรจำไว้และพยายามระวัง ทุกฟังก์ชันควบคุมโฟลว์ที่เราสร้างมาจนถึงตอนนี้ล้วนเป็นสัญญาณอนุพัทธ์โดยพื้นฐาน นั่นคือมันจะรันซ้ำทุกครั้งที่ค่าเปลี่ยน ในตัวอย่างข้างต้น ที่ค่าเปลี่ยนสลับกันระหว่างคู่กับคี่ทุกครั้ง แบบนี้ก็ใช้ได้

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

แบบนี้ *ได้ผล* แน่นอน แต่ถ้าคุณเพิ่มล็อกเข้าไป คุณอาจประหลาดใจ

```rust
let message = move || if value.get() > 5 {
    logging::log!("{}: rendering Big", value.get());
    "Big"
} else {
    logging::log!("{}: rendering Small", value.get());
    "Small"
};
```

เมื่อผู้ใช้คลิกปุ่มเพิ่มค่า `value` ซ้ำๆ คุณจะเห็นอะไรทำนองนี้:

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

ทุกครั้งที่ `value` เปลี่ยน มันจะรันคำสั่ง `if` ซ้ำ ซึ่งก็สมเหตุสมผลกับวิธีการทำงานของรีแอกทิวิตี แต่มันมีข้อเสีย สำหรับโหนดข้อความง่ายๆ การรันคำสั่ง `if` ซ้ำและเรนเดอร์ใหม่ก็ไม่ใช่เรื่องใหญ่ แต่ลองจินตนาการว่ามันเป็นแบบนี้ดู:

```rust
let message = move || if value.get() > 5 {
    <Big/>
} else {
    <Small/>
};
```

แบบนี้จะเรนเดอร์ `<Small/>` ซ้ำห้าครั้ง แล้วเรนเดอร์ `<Big/>` ซ้ำไปเรื่อยๆ ไม่จบ ถ้าคอมโพเนนต์เหล่านั้นกำลังโหลดรีซอร์ส สร้างสัญญาณ หรือแค่สร้างโหนด DOM นี่ก็เป็นงานที่เกินความจำเป็น

### `<Show/>`

คอมโพเนนต์ [`<Show/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.Show.html) คือคำตอบ คุณส่งฟังก์ชันเงื่อนไข `when` ให้มัน, `fallback` ที่จะแสดงถ้าฟังก์ชัน `when` คืนค่า `false` และลูก (children) ที่จะเรนเดอร์ถ้า `when` เป็น `true`

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

`<Show/>` ทำการเมโมไมซ์เงื่อนไข `when` จึงเรนเดอร์ `<Small/>` เพียงครั้งเดียว และแสดงคอมโพเนนต์เดิมต่อไปจนกว่า `value` จะมากกว่าห้า จากนั้นจึงเรนเดอร์ `<Big/>` ครั้งเดียว และแสดงต่อไปเรื่อยๆ จนกว่า `value` จะลดลงต่ำกว่าห้า แล้วจึงเรนเดอร์ `<Small/>` อีกครั้ง

นี่เป็นเครื่องมือที่มีประโยชน์เพื่อหลีกเลี่ยงการเรนเดอร์ซ้ำเมื่อใช้นิพจน์ `if` แบบไดนามิก เช่นเคย มันมีโอเวอร์เฮดอยู่บ้าง สำหรับโหนดง่ายๆ มากๆ (อย่างการอัปเดตโหนดข้อความตัวเดียว หรืออัปเดตคลาสหรือแอตทริบิวต์) `move || if ...` จะมีประสิทธิภาพมากกว่า แต่ถ้าการเรนเดอร์สาขาใดสาขาหนึ่งมีค่าใช้จ่ายสูงล่ะก็ ให้ใช้ `<Show/>` เถอะ

## หมายเหตุ: การแปลงชนิดข้อมูล

ยังมีอีกเรื่องสุดท้ายที่สำคัญต้องกล่าวถึงในหัวข้อนี้

Leptos ใช้ทรีวิวแบบไทป์สแตติก (statically-typed) มาโคร `view` คืนค่าชนิดข้อมูลที่แตกต่างกันสำหรับวิวชนิดต่างๆ

โค้ดนี้จะคอมไพล์ไม่ผ่าน เพราะเอลิเมนต์ HTML ที่ต่างกันมีชนิดข้อมูลที่ต่างกัน

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

การเป็นไทป์ที่เข้มงวดนี้ทรงพลังมาก เพราะมันเปิดทางให้มีการปรับปรุงประสิทธิภาพตอนคอมไพล์ได้สารพัด แต่ในตรรกะแบบมีเงื่อนไขแบบนี้อาจน่ารำคาญสักหน่อย เพราะใน Rust คุณไม่สามารถคืนค่าชนิดข้อมูลที่ต่างกันจากสาขาต่างๆ ของเงื่อนไขได้ มีสองวิธีที่จะพาคุณออกจากสถานการณ์นี้:

1. ใช้ enum `Either` (และ `EitherOf3`, `EitherOf4` ฯลฯ) เพื่อแปลงชนิดข้อมูลที่ต่างกันให้เป็นชนิดเดียวกัน
2. ใช้ `.into_any()` เพื่อแปลงหลายชนิดข้อมูลให้เป็น `AnyView` ที่ลบข้อมูลชนิดออก (type-erased) ตัวเดียว

นี่คือตัวอย่างเดิม แต่เพิ่มการแปลงชนิดเข้าไปแล้ว:

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
