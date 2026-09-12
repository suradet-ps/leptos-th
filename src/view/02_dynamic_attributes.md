# `view`: คลาส สไตล์ และแอตทริบิวต์แบบไดนามิก

จนถึงตอนนี้ เราได้เห็นวิธีใช้มาโคร `view` เพื่อสร้างตัวรับฟังเหตุการณ์ และ
สร้างข้อความแบบไดนามิกโดยการส่งฟังก์ชัน (เช่น สัญญาณ) เข้าไปในวิวแล้ว

แต่แน่นอนว่า ยังมีอย่างอื่นอีกที่คุณอาจต้องการอัปเดตในส่วนติดต่อผู้ใช้ของคุณ
ในส่วนนี้ เราจะมาดูวิธีอัปเดตคลาส สไตล์ และแอตทริบิวต์แบบไดนามิก
และเราจะแนะนำแนวคิดของ**สัญญาณอนุพัทธ์ (derived signal)**

เรามาเริ่มด้วยคอมโพเนนต์ง่ายๆ ที่คุณน่าจะคุ้นเคย: คลิกปุ่มเพื่อ
เพิ่มตัวนับขึ้นหนึ่ง

```rust
#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);

    view! {
        <button
            on:click=move |_| {
                *set_count.write() += 1;
            }
        >
            "Click me: "
            {count}
        </button>
    }
}
```

จนถึงตอนนี้ เราได้ครอบคลุมทั้งหมดนี้ไปแล้วในบทที่แล้ว

## คลาสแบบไดนามิก

ทีนี้สมมติว่าผมอยากอัปเดตรายการคลาส CSS บนเอลิเมนต์นี้แบบไดนามิก
ตัวอย่างเช่น สมมติว่าผมต้องการเพิ่มคลาส `red` เมื่อค่าตัวนับเป็นเลขคี่ ผมสามารถ
ทำได้โดยใช้ไวยากรณ์ `class:`

```rust
class:red=move || count.get() % 2 == 1
```

แอตทริบิวต์ `class:` ประกอบด้วย

1. ชื่อคลาสที่อยู่ถัดจากเครื่องหมายโคลอน (`red`)
2. ค่าซึ่งอาจเป็น `bool` หรือฟังก์ชันที่คืนค่า `bool`

เมื่อค่าเป็น `true` คลาสจะถูกเพิ่ม เมื่อค่าเป็น `false` คลาส
จะถูกลบออก และหากค่าเป็นฟังก์ชันที่เข้าถึงสัญญาณ คลาสนั้น
จะอัปเดตแบบรีแอกทีฟเมื่อสัญญาณเปลี่ยนแปลง

ตอนนี้ทุกครั้งที่ผมคลิกปุ่ม ข้อความควรสลับระหว่างสีแดงกับสีดำ
เมื่อตัวเลขสลับระหว่างเลขคู่กับเลขคี่

```rust
<button
    on:click=move |_| {
        *set_count.write() += 1;
    }
    // the class: syntax reactively updates a single class
    // here, we'll set the `red` class when `count` is odd
    class:red=move || count.get() % 2 == 1
>
    "Click me"
</button>
```

> หากคุณกำลังทำตามอยู่ อย่าลืมเข้าไปใน `index.html` ของคุณแล้วเพิ่มอะไรทำนองนี้:
>
> ```html
> <style>
>   .red {
>     color: red;
>   }
> </style>
> ```

ชื่อคลาส CSS บางชื่อไม่สามารถถูกพาร์สโดยตรงโดยมาโคร `view` ได้ โดยเฉพาะถ้ามีทั้งขีดกลางและตัวเลขหรืออักขระอื่นปนกัน ในกรณีนั้น คุณสามารถใช้ไวยากรณ์แบบทูเพิลได้: `class=("name", value)` ซึ่งยังคงอัปเดตคลาสเดียวโดยตรง

```rust
class=("button-20", move || count.get() % 2 == 1)
```

ไวยากรณ์แบบทูเพิลยังช่วยให้ระบุหลายคลาสภายใต้เงื่อนไขเดียวได้ โดยใช้อาร์เรย์เป็นสมาชิกตัวแรกของทูเพิล

```rust
class=(["button-20", "rounded"], move || count.get() % 2 == 1)
```

## สไตล์แบบไดนามิก

พร็อพเพอร์ตี CSS แต่ละตัวสามารถอัปเดตได้โดยตรงด้วยไวยากรณ์ `style:` ที่คล้ายกัน

```rust
let (count, set_count) = signal(0);

view! {
    <button
        on:click=move |_| {
            *set_count.write() += 10;
        }
        // set the `style` attribute
        style="position: absolute"
        // and toggle individual CSS properties with `style:`
        style:left=move || format!("{}px", count.get() + 100)
        style:background-color=move || format!("rgb({}, {}, 100)", count.get(), 100)
        style:max-width="400px"
        // Set a CSS variable for stylesheet use
        style=("--columns", move || count.get().to_string())
    >
        "Click to Move"
    </button>
}
```

## แอตทริบิวต์แบบไดนามิก

หลักการเดียวกันนี้ใช้กับแอตทริบิวต์ทั่วไปด้วย การส่งสตริงธรรมดาหรือค่าพริมิตีฟ
ให้กับแอตทริบิวต์จะทำให้มันมีค่าคงที่ การส่งฟังก์ชัน (รวมถึงสัญญาณ)
ให้กับแอตทริบิวต์จะทำให้มันอัปเดตค่าแบบรีแอกทีฟ เรามาเพิ่มเอลิเมนต์
อีกตัวลงในวิวของเรากัน:

```rust
<progress
    max="50"
    // signals are functions, so `value=count` and `value=move || count.get()`
    // are interchangeable.
    value=count
/>
```

ตอนนี้ทุกครั้งที่เราตั้งค่าตัวนับ ไม่เพียงแต่ `class` ของ `<button>` จะ
สลับไปมาเท่านั้น แต่ `value` ของแถบ `<progress>` ก็จะเพิ่มขึ้นด้วย ซึ่งหมายความว่า
แถบความคืบหน้าของเราจะขยับไปข้างหน้า

## สัญญาณอนุพัทธ์ (derived signal)

เรามาลงลึกอีกชั้นกันเล่นๆ สักหน่อย

คุณรู้อยู่แล้วว่า เราสร้างส่วนติดต่อผู้ใช้แบบรีแอกทีฟได้เพียงแค่ส่งฟังก์ชันเข้าไป
ใน `view` นั่นหมายความว่าเราสามารถเปลี่ยนแถบความคืบหน้าของเราได้ง่ายๆ ตัวอย่างเช่น
สมมติว่าเราต้องการให้มันเคลื่อนที่เร็วเป็นสองเท่า:

```rust
<progress
    max="50"
    value=move || count.get() * 2
/>
```

แต่ลองจินตนาการว่าเราต้องการใช้การคำนวณนั้นซ้ำในมากกว่าหนึ่งที่ คุณทำได้
โดยใช้**สัญญาณอนุพัทธ์ (derived signal)**: โคลเชอร์ที่เข้าถึงสัญญาณ

```rust
let double_count = move || count.get() * 2;

/* insert the rest of the view */
<progress
    max="50"
    // we use it once here
    value=double_count
/>
<p>
    "Double Count: "
    // and again here
    {double_count}
</p>
```

สัญญาณอนุพัทธ์ช่วยให้คุณสร้างค่ารีแอกทีฟที่คำนวณไว้แล้ว ซึ่งสามารถใช้ในหลาย
ที่ในแอปพลิเคชันของคุณโดยมีค่าใช้จ่ายน้อยที่สุด

หมายเหตุ: การใช้สัญญาณอนุพัทธ์แบบนี้หมายความว่าการคำนวณจะรันหนึ่งครั้งต่อ
การเปลี่ยนแปลงของสัญญาณ (เมื่อ `count()` เปลี่ยน) และอีกหนึ่งครั้งต่อที่ที่เราเข้าถึง `double_count`
กล่าวอีกนัยหนึ่งคือสองครั้ง นี่เป็นการคำนวณที่ถูกมาก จึงไม่มีปัญหา
เราจะดูเมโม (memo) ในบทถัดไป ซึ่งออกแบบมาเพื่อแก้ปัญหานี้
สำหรับการคำนวณที่มีค่าใช้จ่ายสูง

> #### หัวข้อขั้นสูง: การแทรก HTML ดิบ
>
> มาโคร `view` รองรับแอตทริบิวต์เพิ่มเติมชื่อ `inner_html` ซึ่ง
> สามารถใช้ตั้งค่าเนื้อหา HTML ของเอลิเมนต์ใดๆ โดยตรงได้ โดยลบ children อื่นๆ
> ที่คุณให้ไว้ทิ้งไปหมด โปรดทราบว่าสิ่งนี้_ไม่_ทำการ escape HTML ที่คุณให้มา คุณ
> ควรตรวจสอบให้แน่ใจว่ามันมีเฉพาะอินพุตที่เชื่อถือได้ หรือเอนทิตี HTML ใดๆ ถูก
> escape ไว้ เพื่อป้องกันการโจมตีแบบ cross-site scripting (XSS)
>
> ```rust
> let html = "<p>This HTML will be injected.</p>";
> view! {
>   <div inner_html=html/>
> }
> ```
>
> [คลิกที่นี่สำหรับเอกสารมาโคร `view` ฉบับเต็ม](https://docs.rs/leptos/latest/leptos/macro.view.html)

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/2-dynamic-attributes-0-7-wddqfp?file=%2Fsrc%2Fmain.rs%3A1%2C1-58%2C1)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/2-dynamic-attributes-0-7-wddqfp?file=%2Fsrc%2Fmain.rs%3A1%2C1-58%2C1" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);

    // a "derived signal" is a function that accesses other signals
    // we can use this to create reactive values that depend on the
    // values of one or more other signals
    let double_count = move || count.get() * 2;

    view! {
        <button
            on:click=move |_| {
                *set_count.write() += 1;
            }
            // the class: syntax reactively updates a single class
            // here, we'll set the `red` class when `count` is odd
            class:red=move || count.get() % 2 == 1
            class=("button-20", move || count.get() % 2 == 1)
        >
            "Click me"
        </button>
        // NOTE: self-closing tags like <br> need an explicit /
        <br/>

        // We'll update this progress bar every time `count` changes
        <progress
            // static attributes work as in HTML
            max="50"

            // passing a function to an attribute
            // reactively sets that attribute
            // signals are functions, so `value=count` and `value=move || count.get()`
            // are interchangeable.
            value=count
        >
        </progress>
        <br/>

        // This progress bar will use `double_count`
        // so it should move twice as fast!
        <progress
            max="50"
            // derived signals are functions, so they can also
            // reactively update the DOM
            value=double_count
        >
        </progress>
        <p>"Count: " {count}</p>
        <p>"Double Count: " {double_count}</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
