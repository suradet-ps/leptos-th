# คอมโพเนนต์พื้นฐาน

“Hello, world!” นั้นเป็นตัวอย่างที่_ง่ายมาก_ ต่อไปเรามาดูสิ่งที่
ใกล้เคียงกับแอปพลิเคชันทั่วไปกันสักหน่อย

ก่อนอื่น เรามาแก้ไขฟังก์ชัน `main` กันก่อน เพื่อให้มันเรนเดอร์เฉพาะ
คอมโพเนนต์ `<App/>` แทนที่จะเรนเดอร์ทั้งแอปพลิเคชัน คอมโพเนนต์เป็นหน่วยพื้นฐานของ
การประกอบและออกแบบในเว็บเฟรมเวิร์กส่วนใหญ่ และ Leptos ก็ไม่มีข้อยกเว้น
ในเชิงแนวคิดแล้ว คอมโพเนนต์คล้ายกับเอลิเมนต์ HTML: มันแทนส่วนหนึ่งของ
DOM ที่มีพฤติกรรมในตัวและชัดเจน ต่างจากเอลิเมนต์ HTML ตรงที่คอมโพเนนต์ใช้
`PascalCase` ดังนั้นแอปพลิเคชัน Leptos ส่วนใหญ่จึงเริ่มต้นด้วยอะไรบางอย่างเช่น
คอมโพเนนต์ `<App/>`

```rust
use leptos::mount::mount_to_body;

fn main() {
    mount_to_body(App);
}
```

ต่อไปเรามานิยามคอมโพเนนต์ `App` ของเราเอง เพราะมันค่อนข้างเรียบง่าย
ผมจะให้โค้ดทั้งหมดก่อน แล้วค่อยพาคุณไล่ดูทีละบรรทัด

```rust
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);

    view! {
        <button
            on:click=move |_| set_count.set(3)
        >
            "Click me: "
            {count}
        </button>
        <p>
            "Double count: "
            {move || count.get() * 2}
        </p>
    }
}
```

## การนำเข้า Prelude

```rust
use leptos::prelude::*;
```

Leptos มี prelude ที่รวบรวมแทรตและฟังก์ชันที่ใช้บ่อยไว้
หากคุณต้องการอิมพอร์ตทีละรายการก็ทำได้เลย คอมไพเลอร์
จะให้คำแนะนำที่เป็นประโยชน์สำหรับการอิมพอร์ตแต่ละรายการ

## ลายเซ็นของคอมโพเนนต์

```rust
#[component]
```

เช่นเดียวกับนิยามคอมโพเนนต์ทั้งหมด ส่วนนี้เริ่มต้นด้วยมาโคร [`#[component]`](https://docs.rs/leptos/latest/leptos/attr.component.html)
โดย `#[component]` จะใส่แอนโนเทชันให้ฟังก์ชันเพื่อให้สามารถใช้เป็นคอมโพเนนต์ในแอปพลิเคชัน Leptos ของคุณได้ เราจะได้เห็นฟีเจอร์อื่นๆ ของ
มาโครนี้ในอีกสองสามบทถัดไป

```rust
fn App() -> impl IntoView
```

ทุกคอมโพเนนต์คือฟังก์ชันที่มีลักษณะดังต่อไปนี้

1. รับอาร์กิวเมนต์ตั้งแต่ศูนย์ตัวขึ้นไป โดยเป็นชนิดใดก็ได้
2. คืนค่า `impl IntoView` ซึ่งเป็นโอเพกชนิดที่ครอบคลุม
   ทุกสิ่งที่คุณสามารถคืนค่าจาก `view` ของ Leptos ได้

> อาร์กิวเมนต์ของฟังก์ชันคอมโพเนนต์จะถูกรวบรวมไว้ในสตรักต์พร็อพ (props) เดียว
> ซึ่งสร้างขึ้นโดยมาโคร `view` ตามความจำเป็น

## เนื้อหาของคอมโพเนนต์

เนื้อหาของฟังก์ชันคอมโพเนนต์คือฟังก์ชันตั้งต้นที่รันเพียงครั้งเดียว ไม่ใช่
ฟังก์ชันเรนเดอร์ที่รันซ้ำหลายครั้ง โดยปกติคุณจะใช้มันเพื่อสร้าง
ตัวแปรรีแอกทีฟสักสองสามตัว นิยามไซด์เอฟเฟกต์ใดๆ ที่ทำงานเมื่อค่าเหล่านั้น
เปลี่ยนแปลง และอธิบายส่วนติดต่อผู้ใช้

```rust
let (count, set_count) = signal(0);
```

[`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html)
สร้างสัญญาณ (signal) ซึ่งเป็นหน่วยพื้นฐานของการเปลี่ยนแปลงแบบรีแอกทีฟและการจัดการสถานะใน Leptos
เมธอดนี้คืนค่าทูเพิล `(getter, setter)` หากต้องการเข้าถึงค่าปัจจุบัน คุณจะ
ใช้ `count.get()` (หรือบน Rust `nightly` ใช้รูปย่อ `count()`) ส่วนการตั้งค่า
ค่าปัจจุบัน คุณจะเรียก `set_count.set(...)` (หรือบน nightly ใช้ `set_count(...)`)

> `.get()` จะโคลนค่าและ `.set()` จะเขียนทับค่า ในหลายกรณี การใช้ `.with()` หรือ `.update()` จะมีประสิทธิภาพมากกว่า ลองดูเอกสารของ [`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) และ [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html) หากคุณอยากเรียนรู้เพิ่มเติมเกี่ยวกับข้อแลกเปลี่ยนเหล่านั้น ณ จุดนี้

## วิว (view)

Leptos นิยามส่วนติดต่อผู้ใช้โดยใช้รูปแบบคล้าย JSX ผ่านมาโคร [`view`](https://docs.rs/leptos/latest/leptos/macro.view.html)

```rust
view! {
    <button
        // define an event listener with on:
        on:click=move |_| set_count.set(3)
    >
        // text nodes are wrapped in quotation marks
        "Click me: "

        // blocks include Rust code
        // in this case, it renders the value of the signal
        {count}
    </button>
    <p>
        "Double count: "
        {move || count.get() * 2}
    </p>
}
```

ส่วนนี้น่าจะเข้าใจได้ไม่ยากนัก: มันดูคล้าย HTML เป็นส่วนใหญ่ โดยมี
ไวยากรณ์ `on:click` พิเศษสำหรับนิยามตัวรับฟังเหตุการณ์ `click` และมี
โหนดข้อความไม่กี่โหนดที่ดูเหมือนสตริง Rust รองรับเอลิเมนต์ HTML ทั้งหมด
รวมถึงทั้งเอลิเมนต์ในตัว (เช่น `<p>`) และเอลิเมนต์ที่กำหนดเอง/เว็บคอมโพเนนต์ (เช่น `<my-custom-element>`)

```admonish info
**ข้อความที่ไม่ใส่เครื่องหมายคำพูด**: มาโคร `view` รองรับโหนดข้อความที่ไม่ใส่เครื่องหมายคำพูดอยู่บ้าง ซึ่งเป็น
เรื่องปกติใน HTML หรือ JSX (กล่าวคือ `<p>Hello!</p>` แทนที่จะเป็น `<p>"Hello!"</p>`) เนื่องจากข้อจำกัดของ
มาโครโปรซีดูรัล (proc macros) ของ Rust การใช้ข้อความที่ไม่ใส่เครื่องหมายคำพูดอาจทำให้เกิดปัญหาเรื่องช่องว่างรอบเครื่องหมายวรรคตอนได้เป็นครั้งคราว และ
ไม่รองรับสตริง Unicode ทั้งหมด คุณจะใช้ข้อความที่ไม่ใส่เครื่องหมายคำพูดก็ได้หากคุณชอบ แต่โปรดทราบว่า
หากคุณพบปัญหาใดๆ กับมัน ปัญหาเหล่านั้นแก้ไขได้เสมอโดยใส่เครื่องหมายคำพูดให้โหนดข้อความให้เป็นสตริง
Rust ธรรมดา
```

แล้วก็มีค่าสองค่าในเครื่องหมายวงเล็บปีกกา: ค่าแรก `{count}` ดูเข้าใจง่ายทีเดียว
(มันก็แค่ค่าของสัญญาณของเรา) แล้วก็...

```rust
{move || count.get() * 2}
```

อะไรก็ไม่รู้

บางครั้งผู้คนก็ล้อกันว่า พวกเขาใช้โคลเชอร์ในแอปพลิเคชัน Leptos แรกของตนเอง
มากกว่าที่เคยใช้ในชีวิตทั้งชีวิต และก็พูดได้เต็มปาก

การส่งฟังก์ชันเข้าไปในวิวเป็นการบอกเฟรมเวิร์กว่า: “นี่คืออะไรบางอย่าง
ที่อาจเปลี่ยนแปลงได้”

เมื่อเราคลิกปุ่มและเรียก `set_count` สัญญาณ `count` ก็จะถูกอัปเดต โคลเชอร์
`move || count.get() * 2` นี้ ซึ่งค่าของมันขึ้นอยู่กับค่าของ `count` จะรันใหม่
และเฟรมเวิร์กจะอัปเดตเฉพาะเจาะจงไปที่โหนดข้อความนั้น โดยไม่แตะต้อง
สิ่งอื่นใดในแอปพลิเคชันของคุณ นี่คือสิ่งที่ทำให้เกิดการอัปเดต
DOM ที่มีประสิทธิภาพสูงมาก

โปรดจำไว้ และนี่คือ_สิ่งที่สำคัญมาก_ มีเพียงสัญญาณและฟังก์ชันเท่านั้นที่ถูกมองว่าเป็นค่ารีแอกทีฟ
ในวิว

นั่นหมายความว่า `{count}` และ `{count.get()}` ทำสิ่งต่างๆ กันมากในวิวของคุณ
`{count}` ส่งสัญญาณเข้าไป บอกให้เฟรมเวิร์กอัปเดตวิวทุกครั้งที่ `count` เปลี่ยนแปลง
`{count.get()}` เข้าถึงค่าของ `count` เพียงครั้งเดียว และส่ง `i32` เข้าไปในวิว
เรนเดอร์มันเพียงครั้งเดียวแบบไม่รีแอกทีฟ

ในทำนองเดียวกัน `{move || count.get() * 2}` และ `{count.get() * 2}` ก็ทำงานต่างกัน
ตัวแรกเป็นฟังก์ชัน จึงเรนเดอร์แบบรีแอกทีฟ ส่วนตัวที่สองเป็นค่า จึง
เรนเดอร์เพียงครั้งเดียว และจะไม่อัปเดตเมื่อ `count` เปลี่ยนแปลง

คุณสามารถเห็นความแตกต่างได้ใน CodeSandbox ด้านล่าง!

เรามาแก้ไขครั้งสุดท้ายกัน `set_count.set(3)` เป็นสิ่งที่ตัวจัดการเหตุการณ์คลิกทำแล้วแทบไม่มีประโยชน์เลย เรามาเปลี่ยนจาก “ตั้งค่านี้เป็น 3” เป็น “เพิ่มค่านี้ขึ้น 1” กัน:

```rust
move |_| {
    *set_count.write() += 1;
}
```

คุณจะเห็นได้ว่าขณะที่ `set_count` เพียงตั้งค่า `set_count.write()` จะให้รีเฟอเรนซ์แบบเปลี่ยนแปลงได้กับเราและกลายพันธุ์ค่าในที่เดิม ไม่ว่าจะใช้วิธีไหนก็จะกระตุ้นการอัปเดตแบบรีแอกทีฟใน UI ของเรา

> ตลอดบทเรียนนี้ เราจะใช้ CodeSandbox เพื่อแสดงตัวอย่างแบบโต้ตอบ
> เพียงวางเมาส์เหนือตัวแปรใดๆ เพื่อดูรายละเอียดจาก Rust-Analyzer
> และเอกสารว่าเกิดอะไรขึ้น คุณสามารถ fork ตัวอย่างไปเล่นด้วยตัวเองได้เต็มที่!

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/1-basic-component-0-7-qvgdxs?file=%2Fsrc%2Fmain.rs%3A1%2C1-59%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

> ในการแสดงเบราว์เซอร์ในแซนด์บ็อกซ์ คุณอาจต้องคลิก `Add DevTools >
Other Previews > 8080.`

<template>
  <iframe src="https://codesandbox.io/p/devbox/1-basic-component-0-7-qvgdxs?file=%2Fsrc%2Fmain.rs%3A1%2C1-59%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// The #[component] macro marks a function as a reusable component
// Components are the building blocks of your user interface
// They define a reusable unit of behavior
#[component]
fn App() -> impl IntoView {
    // here we create a reactive signal
    // and get a (getter, setter) pair
    // signals are the basic unit of change in the framework
    // we'll talk more about them later
    let (count, set_count) = signal(0);

    // the `view` macro is how we define the user interface
    // it uses an HTML-like format that can accept certain Rust values
    view! {
        <button
            // on:click will run whenever the `click` event fires
            // every event handler is defined as `on:{eventname}`

            // we're able to move `set_count` into the closure
            // because signals are Copy and 'static

            on:click=move |_| *set_count.write() += 1
        >
            // text nodes in RSX should be wrapped in quotes,
            // like a normal Rust string
            "Click me: "
            {count}
        </button>
        <p>
            <strong>"Reactive: "</strong>
            // you can insert Rust expressions as values in the DOM
            // by wrapping them in curly braces
            // if you pass in a function, it will reactively update
            {move || count.get()}
        </p>
        <p>
            <strong>"Reactive shorthand: "</strong>
            // you can use signals directly in the view, as a shorthand
            // for a function that just wraps the getter
            {count}
        </p>
        <p>
            <strong>"Not reactive: "</strong>
            // NOTE: if you just write {count.get()}, this will *not* be reactive
            // it simply gets the value of count once
            {count.get()}
        </p>
    }
}

// This `main` function is the entry point into the app
// It just mounts our component to the <body>
// Because we defined it as `fn App`, we can now use it in a
// template as <App/>
fn main() {
    leptos::mount::mount_to_body(App)
}
```
</details>
