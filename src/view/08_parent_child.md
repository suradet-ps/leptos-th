# การสื่อสารระหว่างคอมโพเนนต์แม่กับลูก

คุณสามารถมองโครงสร้างแอปพลิเคชันของคุณเป็นแผนผังต้นไม้ (tree) ของคอมโพเนนต์ที่ซ้อนกันอยู่ แต่ละคอมโพเนนต์จะจัดการสถานะภายในของตัวเองและดูแลส่วนหนึ่งของหน้าตาผู้ใช้ (UI) ทำให้คอมโพเนนต์แต่ละตัวมักมีความเป็นอิสระต่อกันค่อนข้างสูง

ทว่าในบางครั้ง คุณย่อมจำเป็นต้องให้คอมโพเนนต์แม่สื่อสารกับคอมโพเนนต์ลูก เช่น สมมติว่าคุณสร้างคอมโพเนนต์ `<FancyButton/>` ซึ่งเพิ่มสไตล์ การบันทึก log หรือการทำงานบางอย่างเสริมให้กับ `<button/>` แล้วคุณต้องการนำ `<FancyButton/>` ไปใช้งานในคอมโพเนนต์ `<App/>` แต่คำถามคือทั้งสองคอมโพเนนต์จะสื่อสารกันได้อย่างไร?

การส่งข้อมูลสถานะจากคอมโพเนนต์แม่ลงไปยังคอมโพเนนต์ลูกนั้นง่ายมาก ซึ่งเราได้เกริ่นถึงเรื่องนี้กันไปบ้างแล้วในบท [คอมโพเนนต์และพร็อพ](./03_components.md) โดยหลักการพื้นฐานคือ หากต้องการให้คอมโพเนนต์แม่สื่อสารลงไปยังคอมโพเนนต์ลูก คุณสามารถส่ง [`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) หรือ [`Signal`](https://docs.rs/leptos/latest/leptos/reactive/wrappers/read/struct.Signal.html) ผ่านพร็อพลงไปได้เลย

แล้วในทิศทางตรงกันข้ามล่ะ? คอมโพเนนต์ลูกจะส่งการแจ้งเตือนเกี่ยวกับเหตุการณ์ หรือการเปลี่ยนแปลงสถานะกลับขึ้นไปยังคอมโพเนนต์แม่ได้อย่างไร?

ใน Leptos มีรูปแบบ (patterns) พื้นฐาน 4 แบบสำหรับการสื่อสารระหว่างคอมโพเนนต์แม่กับลูก:

## 1. ส่ง [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html)

วิธีแรกคือการส่ง `WriteSignal` จากคอมโพเนนต์แม่ลงไปยังคอมโพเนนต์ลูก แล้วให้อัปเดตค่าจากภายในคอมโพเนนต์ลูกโดยตรง วิธีนี้ช่วยให้คุณแก้ไขสถานะของคอมโพเนนต์แม่จากภายในคอมโพเนนต์ลูกได้ทันที

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);
    view! {
        <p>"Toggled? " {toggled}</p>
        <ButtonA setter=set_toggled/>
    }
}

#[component]
pub fn ButtonA(setter: WriteSignal<bool>) -> impl IntoView {
    view! {
        <button
            on:click=move |_| setter.update(|value| *value = !*value)
        >
            "Toggle"
        </button>
    }
}
```

รูปแบบนี้เรียบง่ายตรงไปตรงมา แต่คุณควรใช้อย่างระมัดระวัง เพราะการส่งต่อ `WriteSignal` กระจายไปทั่วอาจทำให้การไล่โค้ดทำความเข้าใจ (reason about) เป็นไปได้ยาก ในตัวอย่างนี้ เมื่ออ่านโค้ดของ `<App/>` ก็ยังพอมองเห็นชัดเจนว่าคุณกำลังมอบสิทธิ์แก้ไขค่า `toggled` ออกไป แต่กลับไม่ชัดเจนเลยว่าค่านั้นจะถูกเปลี่ยนเมื่อไรหรืออย่างไร ในตัวอย่างเล็ก ๆ ที่จำกัดขอบเขตเช่นนี้อาจเข้าใจง่าย แต่หากคุณเริ่มส่ง `WriteSignal` กระจายไปทั่วทั้งโปรเจกต์ คุณควรพิจารณาอย่างจริงจังว่ามันจะนำไปสู่โค้ดที่พันกันยุ่งเหยิง (spaghetti code) หรือไม่

## 2. ใช้คอลแบ็ก

อีกวิธีหนึ่งคือการส่งฟังก์ชันคอลแบ็ก (callback) ไปยังคอมโพเนนต์ลูก เช่น พร็อพ `on_click`

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);
    view! {
        <p>"Toggled? " {toggled}</p>
        <ButtonB on_click=move |_| set_toggled.update(|value| *value = !*value)/>
    }
}

#[component]
pub fn ButtonB(on_click: impl FnMut(MouseEvent) + 'static) -> impl IntoView {
    view! {
        <button on:click=on_click>
            "Toggle"
        </button>
    }
}
```

คุณจะสังเกตเห็นว่า ในขณะที่ `<ButtonA/>` ได้รับ `WriteSignal` ไปและเป็นผู้ตัดสินใจเองว่าจะแก้ไขค่านั้นอย่างไร แต่ `<ButtonB/>` เพียงแค่ส่งสัญญาณเหตุการณ์ (fire event) ออกมาเท่านั้น โดยโลจิกการอัปเดตสถานะทั้งหมดยังคงเกิดขึ้นที่ `<App/>` วิธีนี้มีข้อดีคือช่วยรักษาให้สถานะยังคงถูกจัดการอยู่ภายในขอบเขตเดิม (local) ซึ่งช่วยป้องกันปัญหา spaghetti code จากการกระจายสิทธิ์แก้ไขสถานะไปทั่ว แต่ก็หมายความว่าโลจิกในการอัปเดตสัญญาณจะต้องอยู่ที่ `<App/>` ด้านบน ไม่ใช่ที่ `<ButtonB/>` ด้านล่าง ซึ่งนี่คือข้อดีข้อเสีย (trade-offs) ในชีวิตจริง ไม่ใช่เรื่องของถูกหรือผิดแบบตายตัว

## 3. ใช้ตัวรับฟังเหตุการณ์

ในความเป็นจริง คุณสามารถเขียนวิธีที่ 2 ในรูปแบบที่ต่างออกไปเล็กน้อยได้ หากคอลแบ็กนั้นตรงกับอีเวนต์เนทีฟของ DOM คุณสามารถเพิ่มตัวรับฟัง `on:` ไปที่จุดเรียกใช้คอมโพเนนต์ภายในมาโคร `view!` ใน `<App/>` ได้โดยตรง

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);
    view! {
        <p>"Toggled? " {toggled}</p>
        // note the on:click instead of on_click
        // this is the same syntax as an HTML element event listener
        <ButtonC on:click=move |_| set_toggled.update(|value| *value = !*value)/>
    }
}

#[component]
pub fn ButtonC() -> impl IntoView {
    view! {
        <button>"Toggle"</button>
    }
}
```

วิธีนี้ช่วยลดปริมาณโค้ดที่คุณต้องเขียนใน `<ButtonC/>` ลงไปได้มากเมื่อเทียบกับ `<ButtonB/>` แถมตัวรับฟังยังได้รับออบเจกต์อีเวนต์ที่มีการระบุชนิดข้อมูลอย่างถูกต้องอีกด้วย กลไกนี้ทำงานโดยการเพิ่มตัวรับฟังอีเวนต์ `on:` ให้กับทุกเอลิเมนต์ระดับบนสุดที่ `<ButtonC/>` คืนค่าออกมา ซึ่งในที่นี้ก็คือ `<button>` เพียงตัวเดียว

แน่นอนว่าวิธีนี้ใช้ได้เฉพาะกับอีเวนต์เนทีฟของ DOM ที่ส่งผ่านลงไปยังเอลิเมนต์ที่เรนเดอร์ในคอมโพเนนต์โดยตรงเท่านั้น สำหรับโลจิกที่ซับซ้อนขึ้นซึ่งไม่ได้ผูกกับเอลิเมนต์ DOM ตรง ๆ (เช่น หากคุณสร้างคอมโพเนนต์ `<ValidatedForm/>` และต้องการคอลแบ็ก `on_valid_form_submit`) คุณควรกลับไปใช้วิธีที่ 2

## 4. การให้คอนเท็กซ์

วิธีนี้เป็นรูปแบบประยุกต์ของวิธีที่ 1 สมมติว่าคุณมีแผนผังคอมโพเนนต์ที่ซ้อนกันลึกหลายชั้น:

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);
    view! {
        <p>"Toggled? " {toggled}</p>
        <Layout/>
    }
}

#[component]
pub fn Layout() -> impl IntoView {
    view! {
        <header>
            <h1>"My Page"</h1>
        </header>
        <main>
            <Content/>
        </main>
    }
}

#[component]
pub fn Content() -> impl IntoView {
    view! {
        <div class="content">
            <ButtonD/>
        </div>
    }
}

#[component]
pub fn ButtonD() -> impl IntoView {
    todo!()
}

```

ในตอนนี้ `<ButtonD/>` ไม่ได้เป็นคอมโพเนนต์ลูกโดยตรงของ `<App/>` อีกต่อไป คุณจึงไม่สามารถส่ง `WriteSignal` ผ่านพร็อพตรง ๆ ได้ง่ายเหมือนเดิม สิ่งที่คุณอาจทำก็คือการส่งพร็อพต่อเป็นทอด ๆ ซึ่งมักเรียกกันว่า "prop drilling" โดยต้องเพิ่มพร็อพให้กับคอมโพเนนต์ทุกชั้นที่อยู่ตรงกลางระหว่างสองตัวนี้:

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);
    view! {
        <p>"Toggled? " {toggled}</p>
        <Layout set_toggled/>
    }
}

#[component]
pub fn Layout(set_toggled: WriteSignal<bool>) -> impl IntoView {
    view! {
        <header>
            <h1>"My Page"</h1>
        </header>
        <main>
            <Content set_toggled/>
        </main>
    }
}

#[component]
pub fn Content(set_toggled: WriteSignal<bool>) -> impl IntoView {
    view! {
        <div class="content">
            <ButtonD set_toggled/>
        </div>
    }
}

#[component]
pub fn ButtonD(set_toggled: WriteSignal<bool>) -> impl IntoView {
    todo!()
}
```

โค้ดแบบนี้จะเริ่มยุ่งเหยิงและเทอะทะ เพราะ `<Layout/>` และ `<Content/>` ไม่ได้มีความจำเป็นต้องใช้ `set_toggled` เลย แต่ต้องรับหน้าที่เป็นทางผ่านเพื่อส่งต่อไปให้ `<ButtonD/>` เท่านั้น ทว่าเรากลับต้องประกาศพร็อพซ้ำซ้อนถึงสามแห่ง ซึ่งนอกจากจะน่ารำคาญแล้วยังทำให้ดูแลรักษายากอีกด้วย ลองนึกภาพว่าหากวันหนึ่งเราเพิ่มตัวเลือกสถานะ เช่น "half-toggled" จนชนิดข้อมูลของ `set_toggled` ต้องเปลี่ยนไปเป็น `enum` เราก็ต้องตามไปแก้พร็อพนี้ถึงสามจุด!

แล้วมีวิธีไหนบ้างไหมที่เราจะสามารถข้ามชั้นเหล่านี้ไปได้เลย?

มีแน่นอน!

### 4.1 คอนเท็กซ์ API

คุณสามารถแชร์ข้อมูลข้ามชั้นโดยไม่ต้องส่งผ่านพร็อพทีละชั้นได้ ด้วยการใช้ฟังก์ชัน [`provide_context`](https://docs.rs/leptos/latest/leptos/context/fn.provide_context.html) และ [`use_context`](https://docs.rs/leptos/latest/leptos/context/fn.use_context.html) คอนเท็กซ์จะถูกระบุด้วยชนิดข้อมูล (Type) ที่คุณส่งเข้าไป (ในตัวอย่างนี้คือ `WriteSignal<bool>`) และคอนเท็กซ์นี้จะไหลลงมาตามลำดับชั้นของแผนผัง UI จากบนลงล่าง ในตัวอย่างนี้ เราสามารถใช้คอนเท็กซ์เพื่อข้ามการทำ prop drilling ที่ไม่จำเป็นทั้งหมดได้

```rust
#[component]
pub fn App() -> impl IntoView {
    let (toggled, set_toggled) = signal(false);

    // share `set_toggled` with all children of this component
    provide_context(set_toggled);

    view! {
        <p>"Toggled? " {toggled}</p>
        <Layout/>
    }
}

// <Layout/> and <Content/> omitted
// To work in this version, drop the `set_toggled` parameter on each

#[component]
pub fn ButtonD() -> impl IntoView {
    // use_context searches up the context tree, hoping to
    // find a `WriteSignal<bool>`
    // in this case, I .expect() because I know I provided it
    let setter = use_context::<WriteSignal<bool>>().expect("to have found the setter provided");

    view! {
        <button
            on:click=move |_| setter.update(|value| *value = !*value)
        >
            "Toggle"
        </button>
    }
}

```

ข้อควรระวังเดียวกันกับที่กล่าวไว้ใน `<ButtonA/>` ยังคงมีผลกับวิธีนี้เช่นกัน: การส่งต่อ `WriteSignal` ควรทำอย่างรอบคอบและระมัดระวัง เพราะมันเปิดโอกาสให้สามารถแก้ไขสถานะจากส่วนใดก็ได้ในโค้ด แต่หากใช้อย่างมีวินัยและรัดกุม นี่ก็เป็นหนึ่งในเทคนิคที่มีประสิทธิภาพสูงสุดสำหรับการจัดการสถานะส่วนกลาง (global state) ใน Leptos เพียงแค่ provide สถานะไว้ที่ระดับบนสุดเท่าที่จำเป็นต้องใช้ แล้วดึงไปใช้ (consume) เฉพาะจุดที่ต้องการในคอมโพเนนต์ด้านล่าง

ข้อดีอีกประการคือ วิธีนี้ไม่มีข้อเสียด้านประสิทธิภาพเลยแม้แต่น้อย เพราะสิ่งที่คุณส่งผ่านคอนเท็กซ์คือสัญญาณรีแอกทีฟแบบละเอียด (fine-grained reactive signal) ดังนั้นคอมโพเนนต์ที่อยู่ตรงกลางระหว่างทาง (`<Layout/>` และ `<Content/>`) _จะไม่ถูกรบกวนหรือเรนเดอร์ใหม่เลย_ เมื่อมีการอัปเดตค่าสัญญาณ คุณกำลังสร้างช่องทางสื่อสารโดยตรงระหว่าง `<ButtonD/>` กับ `<App/>` ยิ่งไปกว่านั้น ด้วยพลังของรีแอกทิวิตีแบบละเอียด คุณกำลังสื่อสารโดยตรงระหว่างการคลิกปุ่มใน `<ButtonD/>` กับโหนดข้อความเพียงโหนดเดียวใน `<App/>` ราวกับว่าคอมโพเนนต์คั่นกลางเหล่านั้นไม่ได้มีอยู่จริง และในความเป็นจริงเมื่อแอปพลิเคชันกำลังทำงาน (runtime) คอมโพเนนต์เหล่านั้นก็ไม่ได้คงอยู่จริง ๆ มีเพียงโครงข่ายของสัญญาณและเอฟเฟกต์ที่เชื่อมต่อกันอยู่เท่านั้น

อย่างไรก็ดี วิธีนี้มีข้อแลกเปลี่ยนสำคัญที่ต้องตระหนักไว้ นั่นคือคุณจะสูญเสียความปลอดภัยของระบบชนิดข้อมูล (type safety) ในระดับคอมไพล์ไทม์ระหว่าง `provide_context` กับ `use_context` ไป เพราะการดึงคอนเท็กซ์ที่ถูกต้องในคอมโพเนนต์ลูกเป็นการตรวจสอบ ณ ตอนรันไทม์ (สังเกตจากการใช้ `use_context.expect(...)`) คอมไพเลอร์จะไม่สามารถช่วยเตือนคุณได้ในระหว่างการรีแฟกเตอร์โค้ดเหมือนกับวิธีส่งผ่านพร็อพตามปกติ

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/8-parent-child-0-7-cgcgk9?file=%2Fsrc%2Fmain.rs%3A1%2C1-116%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/8-parent-child-0-7-cgcgk9?file=%2Fsrc%2Fmain.rs%3A1%2C1-116%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::{ev::MouseEvent, prelude::*};

// This highlights four different ways that child components can communicate
// with their parent:
// 1) <ButtonA/>: passing a WriteSignal as one of the child component props,
//    for the child component to write into and the parent to read
// 2) <ButtonB/>: passing a closure as one of the child component props, for
//    the child component to call
// 3) <ButtonC/>: adding an `on:` event listener to a component
// 4) <ButtonD/>: providing a context that is used in the component (rather than prop drilling)

#[derive(Copy, Clone)]
struct SmallcapsContext(WriteSignal<bool>);

#[component]
pub fn App() -> impl IntoView {
    // just some signals to toggle four classes on our <p>
    let (red, set_red) = signal(false);
    let (right, set_right) = signal(false);
    let (italics, set_italics) = signal(false);
    let (smallcaps, set_smallcaps) = signal(false);

    // the newtype pattern isn't *necessary* here but is a good practice
    // it avoids confusion with other possible future `WriteSignal<bool>` contexts
    // and makes it easier to refer to it in ButtonD
    provide_context(SmallcapsContext(set_smallcaps));

    view! {
        <main>
            <p
                // class: attributes take F: Fn() => bool, and these signals all implement Fn()
                class:red=red
                class:right=right
                class:italics=italics
                class:smallcaps=smallcaps
            >
                "Lorem ipsum sit dolor amet."
            </p>

            // Button A: pass the signal setter
            <ButtonA setter=set_red/>

            // Button B: pass a closure
            <ButtonB on_click=move |_| set_right.update(|value| *value = !*value)/>

            // Button C: use a regular event listener
            // setting an event listener on a component like this applies it
            // to each of the top-level elements the component returns
            <ButtonC on:click=move |_| set_italics.update(|value| *value = !*value)/>

            // Button D gets its setter from context rather than props
            <ButtonD/>
        </main>
    }
}

/// Button A receives a signal setter and updates the signal itself
#[component]
pub fn ButtonA(
    /// Signal that will be toggled when the button is clicked.
    setter: WriteSignal<bool>,
) -> impl IntoView {
    view! {
        <button
            on:click=move |_| setter.update(|value| *value = !*value)
        >
            "Toggle Red"
        </button>
    }
}

/// Button B receives a closure
#[component]
pub fn ButtonB(
    /// Callback that will be invoked when the button is clicked.
    on_click: impl FnMut(MouseEvent) + 'static,
) -> impl IntoView
{
    view! {
        <button
            on:click=on_click
        >
            "Toggle Right"
        </button>
    }
}

/// Button C is a dummy: it renders a button but doesn't handle
/// its click. Instead, the parent component adds an event listener.
#[component]
pub fn ButtonC() -> impl IntoView {
    view! {
        <button>
            "Toggle Italics"
        </button>
    }
}

/// Button D is very similar to Button A, but instead of passing the setter as a prop
/// we get it from the context
#[component]
pub fn ButtonD() -> impl IntoView {
    let setter = use_context::<SmallcapsContext>().unwrap().0;

    view! {
        <button
            on:click=move |_| setter.update(|value| *value = !*value)
        >
            "Toggle Small Caps"
        </button>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
