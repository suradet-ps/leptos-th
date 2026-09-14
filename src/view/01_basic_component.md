# คอมโพเนนต์พื้นฐาน

ตัวอย่าง “Hello, world!” นั้นเรียบง่ายมาก คราวนี้เรามาลองดูสิ่งที่ใกล้เคียงกับแอปพลิเคชันจริงกันสักหน่อย

ก่อนอื่น เรามาแก้ไขฟังก์ชัน `main` เพื่อให้ทำหน้าที่เมานต์คอมโพเนนต์ `<App/>` แทนที่จะเรนเดอร์ข้อความตรงๆ ลงไปในบอดี้ คอมโพเนนต์คือหน่วยพื้นฐานของการประกอบส่วนติดต่อผู้ใช้ (UI) ในเว็บเฟรมเวิร์กส่วนใหญ่ และ Leptos ก็เช่นเดียวกัน ในเชิงแนวคิด คอมโพเนนต์จะคล้ายกับเอลิเมนต์ของ HTML: นั่นคือเป็นตัวแทนของส่วนหนึ่งในโครงสร้าง DOM ที่มีพฤติกรรมในตัวอย่างชัดเจน จุดแตกต่างคือคอมโพเนนต์จะใช้รูปแบบชื่อแบบ `PascalCase` ดังนั้น แอปพลิเคชัน Leptos ส่วนใหญ่จึงเริ่มต้นด้วยคอมโพเนนต์รากอย่าง `<App/>`

```rust
use leptos::mount::mount_to_body;

fn main() {
    mount_to_body(App);
}
```

ต่อไป เรามานิยามคอมโพเนนต์ `App` ของเราเอง เนื่องจากโค้ดมีขนาดกะทัดรัดและตรงไปตรงมา เราจะดูโค้ดภาพรวมทั้งหมดก่อน แล้วค่อยมาเจาะลึกการทำงานทีละบรรทัดด้วยกัน:

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

Leptos ได้จัดเตรียม prelude ที่รวบรวม Trait และฟังก์ชันสำคัญที่ใช้งานบ่อยไว้ให้ครบถ้วน หากคุณต้องการเลือก import ทีละรายการด้วยตนเองก็ทำได้เช่นกัน โดยคอมไพเลอร์ของ Rust จะคอยแนะนำชื่อโมดูลและแทรตที่เกี่ยวข้องให้อย่างชัดเจน

## รูปแบบซิกเนเจอร์ของคอมโพเนนต์

```rust
#[component]
```

เช่นเดียวกับนิยามคอมโพเนนต์ทั้งหมด ส่วนนี้จะเริ่มต้นด้วยมาโคร [`#[component]`](https://docs.rs/leptos/latest/leptos/attr.component.html) เพื่อแอนโนเทตฟังก์ชันธรรมดาให้กลายเป็นคอมโพเนนต์ที่ระบบของ Leptos รู้จักและนำไปใช้งานในแอปพลิเคชันได้ เราจะได้เรียนรู้ฟีเจอร์อื่นๆ ของมาโครนี้เพิ่มเติมในบทถัดๆ ไป

```rust
fn App() -> impl IntoView
```

ทุกคอมโพเนนต์ใน Leptos คือฟังก์ชันที่มีคุณลักษณะสำคัญดังต่อไปนี้:

1. รับพารามิเตอร์ตั้งแต่ศูนย์ตัวขึ้นไป (เป็นชนิดข้อมูลใดก็ได้)
2. คืนค่าเป็น `impl IntoView` ซึ่งเป็นชนิดข้อมูลแบบทึบ (opaque type) ที่ครอบคลุมทุกสิ่งที่สามารถนำไปแสดงผลใน `view` ของ Leptos ได้

> พารามิเตอร์ทั้งหมดของฟังก์ชันคอมโพเนนต์จะถูกรวบรวมเข้าเป็นโครงสร้างพร็อพ (props struct) เดียวโดยอัตโนมัติ ซึ่งมาโคร `view` จะสร้างขึ้นมาจัดการให้ตามความเหมาะสม

## ส่วนเนื้อหาของคอมโพเนนต์ (The Component Body)

เนื้อหาภายในฟังก์ชันคอมโพเนนต์แท้จริงแล้วคือฟังก์ชันเซ็ตอัป (setup function) ที่จะถูกรันเพียงครั้งเดียวเท่านั้น **ไม่ใช่**ฟังก์ชันเรนเดอร์ที่จะถูกเรียกซ้ำไปซ้ำมาหลายรอบ โดยทั่วไปคุณจะใช้พื้นที่ส่วนนี้ในการประกาศตัวแปรรีแอกทีฟ กำหนดไซด์เอฟเฟกต์ที่ต้องตอบสนองเมื่อข้อมูลเปลี่ยน และอธิบายโครงสร้างหน้าตาของ UI

```rust
let (count, set_count) = signal(0);
```

ฟังก์ชัน [`signal`](https://docs.rs/leptos/latest/leptos/reactive/signal/fn.signal.html) ทำหน้าที่สร้างสัญญาณ (signal) ซึ่งเป็นหน่วยพื้นฐานของการเปลี่ยนแปลงแบบรีแอกทีฟและการจัดการสถานะใน Leptos โดยจะคืนค่าออกมาเป็นทูเพิลคู่ `(getter, setter)` หากต้องการอ่านค่าปัจจุบัน ให้เรียกใช้ `count.get()` (หรือบน Rust `nightly` สามารถใช้รูปย่อ `count()`) และหากต้องการตั้งค่าใหม่ ให้เรียกคำสั่ง `set_count.set(...)` (หรือบน nightly คือ `set_count(...)`)

> เมธอด `.get()` จะทำการโคลนค่าออกมา และ `.set()` จะเขียนทับค่าเดิม ในหลายกรณี การใช้ `.with()` หรือ `.update()` จะมีประสิทธิภาพสูงกว่ามาก ลองศึกษาเอกสารของ [`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) และ [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html) หากคุณต้องการทำความเข้าใจข้อแลกเปลี่ยนเหล่านี้เพิ่มเติม

## ส่วนการแสดงผล (The View)

Leptos นิยามส่วนติดต่อผู้ใช้ด้วยไวยากรณ์คล้าย JSX ผ่านมาโคร [`view`](https://docs.rs/leptos/latest/leptos/macro.view.html)

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

โครงสร้างตรงนี้น่าจะคุ้นเคยเป็นอย่างดีสำหรับคนที่เคยเขียนเว็บ: หน้าตาจะคล้ายกับ HTML เกือบทั้งหมด โดยมีไวยากรณ์พิเศษ `on:click` สำหรับผูกตัวรับฟังเหตุการณ์ (event listener) ของการคลิก และโหนดข้อความจะถูกครอบด้วยเครื่องหมายคำพูดเหมือนสตริงใน Rust ทั้งนี้ Leptos รองรับเอลิเมนต์ HTML มาตรฐานทั้งหมด ทั้งแท็กในตัว (เช่น `<p>`) และเอลิเมนต์แบบกำหนดเองหรือ Web Components (เช่น `<my-custom-element>`)

```admonish info
**ข้อความที่ไม่ใส่เครื่องหมายคำพูด**: มาโคร `view` รองรับโหนดข้อความแบบไม่ใส่เครื่องหมายคำพูดอยู่บ้าง เพื่อให้คุ้นมือเหมือนการเขียน HTML หรือ JSX ทั่วไป (เช่น `<p>Hello!</p>` แทนที่จะต้องเขียน `<p>"Hello!"</p>`) แต่เนื่องจากข้อจำกัดของโพรซีเดอรัลมาโคร (proc macros) ในภาษา Rust การละเครื่องหมายคำพูดอาจทำให้การเว้นวรรครอบเครื่องหมายวรรคตอนคลาดเคลื่อนได้เป็นครั้งคราว และยังไม่รองรับสตริง Unicode ครบทุกรูปแบบ คุณสามารถเลือกเขียนแบบไม่ใส่เครื่องหมายคำพูดได้ตามความชอบ แต่หากพบปัญหาในการแสดงผล เพียงใส่เครื่องหมายคำพูดครอบข้อความให้กลายเป็นสตริง Rust ธรรมดาก็จะแก้ปัญหาได้เสมอ
```

จากนั้น เราจะเห็นค่าที่อยู่ในเครื่องหมายปีกกาสองจุด: จุดแรกคือ `{count}` ซึ่งตรงไปตรงมามาก (เป็นเพียงการนำค่าของสัญญาณมาแสดงผล) ส่วนจุดถัดมาคือ...

```rust
{move || count.get() * 2}
```

หลายคนมักพูดติดตลกว่า ในการเขียนแอปแรกด้วย Leptos พวกเขาได้เขียน closure มากกว่าที่เคยเขียนมาทั้งชีวิตเสียอีก ซึ่งก็ไม่ใช่เรื่องเกินจริงเลย

**การส่งฟังก์ชันเข้าไปในวิว คือการบอกกับเฟรมเวิร์กว่า: "ตรงนี้คือค่าที่สามารถเปลี่ยนแปลงได้นะ"**

เมื่อเราคลิกปุ่มและสั่ง `set_count` ตัวสัญญาณ `count` จะถูกอัปเดต โคลเชอร์ `move || count.get() * 2` ซึ่งมีค่าผูกอยู่กับ `count` จะถูกสั่งให้คำนวณใหม่ และเฟรมเวิร์กจะทำการอัปเดตแบบเจาะจงเฉพาะโหนดข้อความจุดนั้นใน DOM โดยตรง โดยไม่แตะต้องส่วนอื่นๆ ของแอปพลิเคชันเลยแม้แต่น้อย นี่คือกลไกเบื้องหลังที่ทำให้การอัปเดต DOM ของ Leptos มีประสิทธิภาพสูงมาก

โปรดจำไว้ว่า — และนี่คือหัวใจที่**สำคัญมาก** — ในมาโคร `view` จะมีเฉพาะ **สัญญาณ (signals)** และ **ฟังก์ชัน (functions)** เท่านั้นที่ระบบจะมองว่าเป็นค่าแบบรีแอกทีฟ

นั่นหมายความว่า `{count}` และ `{count.get()}` ให้ผลลัพธ์ที่แตกต่างกันอย่างสิ้นเชิงในวิวของคุณ:
- `{count}` ส่งตัวสัญญาณเข้าไป บอกให้เฟรมเวิร์กคอยอัปเดตวิวทุกครั้งที่ค่าของ `count` เปลี่ยนไป
- `{count.get()}` เป็นเพียงการอ่านค่าของ `count` ออกมา ณ วินาทีนั้น แล้วส่งตัวเลข `i32` ธรรมดาเข้าไปในวิว ซึ่งจะเรนเดอร์เพียงรอบเดียวและไม่มีการอัปเดตแบบรีแอกทีฟอีก

ในทำนองเดียวกัน `{move || count.get() * 2}` กับ `{count.get() * 2}` ก็ทำงานต่างกัน:
ตัวแรกเป็นฟังก์ชัน จึงเรนเดอร์แบบรีแอกทีฟและอัปเดตตามสัญญาณ ส่วนตัวหลังเป็นเพียงการคำนวณค่าตัวเลขรอบเดียว จึงไม่ตอบสนองเมื่อ `count` เปลี่ยนแปลง

คุณสามารถทดลองดูความแตกต่างนี้ได้ในตัวอย่าง CodeSandbox ด้านล่างนี้!

ก่อนจะจบบทนี้ เรามาปรับโค้ดกันอีกจุดหนึ่ง: การเขียน `set_count.set(3)` ในอีเวนต์คลิกดูไม่ค่อยมีประโยชน์ในแอปจริงเท่าไร เรามาเปลี่ยนจากการ "ตั้งค่าให้เป็น 3" เป็นการ "เพิ่มค่าขึ้นทีละ 1" กันดีกว่า:

```rust
move |_| {
    *set_count.write() += 1;
}
```

ตรงนี้จะเห็นว่า ในขณะที่ `set_count` ทำหน้าที่เขียนทับค่าใหม่ลงไป เมธอด `set_count.write()` จะคืนค่าเป็น mutable reference ทำให้เราสามารถแก้ไขค่าในหน่วยความจำเดิม (mutate in-place) ได้โดยตรง ซึ่งทั้งสองวิธีต่างส่งสัญญาณกระตุ้นการอัปเดตแบบรีแอกทีฟบน UI ได้เหมือนกัน

> ตลอดทั้งหนังสือเล่มนี้ เราจะใช้ CodeSandbox ในการแสดงตัวอย่างแบบโต้ตอบได้
> คุณสามารถนำเมาส์ไปชี้เหนือตัวแปรต่างๆ เพื่อดูรายละเอียดจาก Rust-Analyzer
> และอ่านเอกสารอธิบายการทำงานได้ทันที รวมถึงสามารถ fork ตัวอย่างไปทดลองเล่นด้วยตัวเองได้อย่างอิสระ!

```admonish sandbox title="Live example" collapsible=true

[Click to open CodeSandbox.](https://codesandbox.io/p/devbox/1-basic-component-0-7-qvgdxs?file=%2Fsrc%2Fmain.rs%3A1%2C1-59%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  Please enable JavaScript to view examples.
</noscript>

> To show the browser in the sandbox, you may need to click `Add DevTools >
Other Previews > 8080.`

<template>
  <iframe src="https://codesandbox.io/p/devbox/1-basic-component-0-7-qvgdxs?file=%2Fsrc%2Fmain.rs%3A1%2C1-59%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>CodeSandbox Source</summary>

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
