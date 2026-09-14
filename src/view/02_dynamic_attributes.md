# `view`: คลาส สไตล์ และแอตทริบิวต์แบบไดนามิก

จนถึงตอนนี้ เราได้เห็นวิธีใช้มาโคร `view!` เพื่อผูกตัวรับฟังเหตุการณ์ (event listeners) และการสร้างข้อความแบบไดนามิกด้วยการส่งฟังก์ชัน (เช่น สัญญาณ) เข้าไปในวิวกันไปแล้ว

แต่นอกจากข้อความแล้ว ยังมีองค์ประกอบอื่นๆ ของ UI อีกมากที่คุณอาจต้องการสั่งให้อัปเดตตามสถานะ ในบทนี้ เราจะมาดูวิธีอัปเดต CSS class, style และ attribute ในแบบไดนามิก พร้อมทั้งแนะนำแนวคิดสำคัญอย่าง **สัญญาณอนุพัทธ์ (derived signal)**

เรามาเริ่มต้นด้วยคอมโพเนนต์ง่ายๆ ที่คุ้นเคย: การคลิกปุ่มเพื่อเพิ่มค่าตัวนับ

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

ถึงตรงนี้ โค้ดทั้งหมดเป็นสิ่งที่เราได้เรียนรู้ไปแล้วในบทที่ผ่านมา

## คลาสแบบไดนามิก

คราวนี้สมมติว่าเราต้องการอัปเดตรายการ CSS class บนปุ่มนี้แบบไดนามิก ตัวอย่างเช่น ต้องการเพิ่มคลาส `red` เข้าไปเมื่อตัวนับเป็นเลขคี่ เราสามารถทำได้ง่ายๆ โดยใช้ไวยากรณ์ `class:`

```rust
class:red=move || count.get() % 2 == 1
```

แอตทริบิวต์ `class:` ประกอบด้วยสองส่วน:

1. ชื่อคลาสที่ต้องการเปิด/ปิด ซึ่งจะต่อท้ายเครื่องหมายโคลอน (`red`)
2. ค่าที่กำหนด ซึ่งอาจเป็นค่า `bool` หรือฟังก์ชันที่คืนค่า `bool`

เมื่อค่าเป็น `true` ระบบจะเพิ่มคลาสนั้นเข้าไปที่เอลิเมนต์ และเมื่อค่าเป็น `false` คลาสนั้นจะถูกนำออก และหากค่านั้นเป็นฟังก์ชันที่อ่านค่ามาจากสัญญาณ ตัวคลาสก็จะอัปเดตตามการเปลี่ยนแปลงของสัญญาณแบบรีแอกทีฟทันที

คราวนี้ ทุกครั้งที่คลิกปุ่ม สีของข้อความจะสลับไปมาระหว่างสีแดงกับสีดำตามเลขคู่และเลขคี่:

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

> หากคุณเขียนโค้ดตามตัวอย่าง อย่าลืมเพิ่มสไตล์ CSS นี้ลงในไฟล์ `index.html` ของคุณด้วย:
>
> ```html
> <style>
>   .red {
>     color: red;
>   }
> </style>
> ```

สำหรับชื่อ CSS class บางชื่อที่ไม่สามารถเขียนต่อท้าย `class:` ได้โดยตรง (เช่น มีเครื่องหมายขีดกลางผสมกับตัวเลขหรืออักขระพิเศษที่มาโคร `view!` แยกคำไม่ได้) คุณสามารถใช้ไวยากรณ์แบบทูเพิลแทนได้: `class=("name", value)` ซึ่งยังคงอัปเดตคลาสเดียวโดยตรง

```rust
class=("button-20", move || count.get() % 2 == 1)
```

นอกจากนี้ ไวยากรณ์ทูเพิลยังเปิดให้คุณผูกหลายคลาสเข้ากับเงื่อนไขเดียวกันได้พร้อมกัน โดยส่งอาเรย์เป็นสมาชิกตัวแรกของทูเพิล:

```rust
class=(["button-20", "rounded"], move || count.get() % 2 == 1)
```

## สไตล์แบบไดนามิก

สำหรับ CSS property แต่ละตัว เราสามารถสั่งอัปเดตค่าโดยตรงได้ด้วยไวยากรณ์ `style:` ในลักษณะที่คล้ายกัน:

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

หลักการเดียวกันนี้ยังใช้ได้กับแอตทริบิวต์ HTML ทั่วไปทั้งหมด: หากเราส่งสตริงธรรมดาหรือค่าคงที่ให้กับแอตทริบิวต์ ค่านั้นก็จะเป็นค่าสถิต (static) แต่หากเราส่งฟังก์ชัน (รวมถึงตัวสัญญาณเอง) ให้กับแอตทริบิวต์ ค่านั้นจะถูกอัปเดตแบบรีแอกทีฟทันทีที่สัญญาณเปลี่ยน ลองเพิ่มเอลิเมนต์ progress bar เข้าไปในวิวของเรา:

```rust
<progress
    max="50"
    // signals are functions, so `value=count` and `value=move || count.get()`
    // are interchangeable.
    value=count
/>
```

ตอนนี้ ทุกครั้งที่เราคลิกปุ่มเพื่อเปลี่ยนค่าตัวนับ ไม่เพียงแต่ `class` ของ `<button>` จะสลับไปมาเท่านั้น แต่ `value` ของแถบ `<progress>` ก็จะเพิ่มขึ้นตามไปด้วย ทำให้แถบความคืบหน้าของเราขยับไปข้างหน้า

## สัญญาณอนุพัทธ์ (derived signal)

เรามาลงลึกขึ้นอีกระดับเพื่อความเข้าใจที่ครอบคลุม

คุณทราบอยู่แล้วว่า เราสร้าง UI แบบรีแอกทีฟได้เพียงแค่ส่งฟังก์ชันเข้าไปใน `view` นั่นหมายความว่าเราสามารถปรับแต่งแถบความคืบหน้าของเราได้อย่างง่ายดาย ตัวอย่างเช่น หากต้องการให้มันเคลื่อนที่เร็วกว่าเดิมเป็นสองเท่า:

```rust
<progress
    max="50"
    value=move || count.get() * 2
/>
```

แต่ลองจินตนาการว่า หากเราต้องการนำการคำนวณ `count.get() * 2` นี้ไปใช้ซ้ำในหลายๆ จุดของแอปพลิเคชัน เราสามารถสร้าง **สัญญาณอนุพัทธ์ (derived signal)** ขึ้นมาได้ ซึ่งก็คือโคลเชอร์ (closure) ที่เข้าถึงสัญญาณตัวอื่น:

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

สัญญาณอนุพัทธ์ช่วยให้คุณสร้างค่าที่คำนวณแบบรีแอกทีฟและนำไปใช้ซ้ำได้หลายที่ทั่วทั้งแอปพลิเคชัน โดยแทบไม่มีภาระประมวลผลส่วนเกิน (overhead) เพิ่มเติมเลย

**ข้อควรทราบ**: การใช้สัญญาณอนุพัทธ์ในลักษณะนี้หมายความว่า การคำนวณจะทำงานหนึ่งครั้งต่อการเปลี่ยนแปลงของสัญญาณ (เมื่อ `count()` เปลี่ยน) และอีกหนึ่งครั้งต่อจุดที่เรานำ `double_count` ไปใช้ (ในตัวอย่างนี้คือ 2 ครั้ง) เนื่องจากการคูณตัวเลขเป็นการคำนวณที่เบามาก จึงไม่มีปัญหาเรื่องประสิทธิภาพ แต่สำหรับการคำนวณที่ซับซ้อนและกินทรัพยากรสูง เราจะได้เรียนรู้เรื่อง Memo ในบทถัดไป ซึ่งออกแบบมาเพื่อแก้ปัญหานี้โดยเฉพาะ

> #### หัวข้อขั้นสูง: การแทรก HTML ดิบ
>
> มาโคร `view` รองรับแอตทริบิวต์พิเศษ `inner_html` ซึ่งใช้สำหรับกำหนดเนื้อหา HTML ดิบให้กับเอลิเมนต์ใดๆ โดยตรง โดยจะลบคอมโพเนนต์ลูกทั้งหมดของเอลิเมนต์นั้นทิ้งไป โปรดระลึกไว้เสมอว่าวิธีนี้จะ_ไม่_ทำการ escape โค้ด HTML ให้ คุณจึงต้องมั่นใจว่าข้อความนั้นมาจากแหล่งข้อมูลที่ปลอดภัยและเชื่อถือได้เท่านั้น หรือต้องผ่านการแปลง HTML entities มาแล้ว เพื่อป้องกันช่องโหว่ความปลอดภัยจากการโจมตีแบบ Cross-Site Scripting (XSS)
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
