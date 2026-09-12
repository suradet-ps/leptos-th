# การสื่อสารระหว่างคอมโพเนนต์แม่กับลูก

คุณสามารถมองแอปพลิเคชันของคุณเป็นแผนผังคอมโพเนนต์ที่ซ้อนกันได้ แต่ละคอมโพเนนต์
จัดการสถานะภายในของตัวเองและดูแลส่วนหนึ่งของส่วนติดต่อผู้ใช้ คอมโพเนนต์
จึงมักเป็นอิสระในตัวเองค่อนข้างมาก

แต่บางครั้ง คุณอาจต้องการสื่อสารระหว่างคอมโพเนนต์แม่กับคอมโพเนนต์ลูก
ตัวอย่างเช่น สมมติว่าคุณนิยามคอมโพเนนต์ `<FancyButton/>` ที่เพิ่มสไตล์ การบันทึกล็อก
หรืออะไรทำนองนั้นให้กับ `<button/>` ไว้ แล้วคุณต้องการใช้ `<FancyButton/>`
ในคอมโพเนนต์ `<App/>` ของคุณ แต่คุณจะสื่อสารระหว่าง
ทั้งสองได้อย่างไร

การสื่อสารสถานะจากคอมโพเนนต์แม่ไปยังคอมโพเนนต์ลูกนั้นง่ายมาก เรา
ได้กล่าวถึงเรื่องนี้บางส่วนในเนื้อหาเกี่ยวกับ [คอมโพเนนต์และพร็อพ](./03_components.md)
โดยพื้นฐานแล้ว ถ้าคุณต้องการให้คอมโพเนนต์แม่สื่อสารกับคอมโพเนนต์ลูก คุณสามารถส่ง
[`ReadSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.ReadSignal.html) หรือ
[`Signal`](https://docs.rs/leptos/latest/leptos/reactive/wrappers/read/struct.Signal.html) เป็นพร็อพได้

แล้วทิศทางกลับกันล่ะ? คอมโพเนนต์ลูกจะส่งการแจ้งเตือนเกี่ยวกับเหตุการณ์
หรือการเปลี่ยนแปลงสถานะกลับขึ้นไปยังคอมโพเนนต์แม่ได้อย่างไร

มีรูปแบบพื้นฐานสี่แบบของการสื่อสารระหว่างคอมโพเนนต์แม่กับลูกใน Leptos

## 1. ส่ง [`WriteSignal`](https://docs.rs/leptos/latest/leptos/reactive/signal/struct.WriteSignal.html)

วิธีหนึ่งก็แค่ส่ง `WriteSignal` จากคอมโพเนนต์แม่ลงไปยังคอมโพเนนต์ลูก แล้วอัปเดต
มันในคอมโพเนนต์ลูก วิธีนี้ช่วยให้คุณจัดการสถานะของคอมโพเนนต์แม่จากคอมโพเนนต์ลูกได้

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

รูปแบบนี้ง่าย แต่คุณควรระวังในการใช้ เพราะการส่ง `WriteSignal`
ไปทั่วอาจทำให้วิเคราะห์โค้ดของคุณได้ยาก ในตัวอย่างนี้ ค่อนข้างชัดเจนเมื่อคุณ
อ่าน `<App/>` ว่าคุณกำลังส่งมอบความสามารถในการแก้ไขค่า `toggled` ต่อออกไป แต่ไม่
ชัดเจนเลยว่ามันจะเปลี่ยนเมื่อไหร่หรืออย่างไร ในตัวอย่างเล็กๆ ที่จำกัดขอบเขตแบบนี้มันเข้าใจได้ง่าย
แต่ถ้าคุณพบว่าตัวเองส่ง `WriteSignal` ไปทั่วโค้ดแบบนี้ คุณควรพิจารณาจริงจัง
ว่ามันทำให้เขียนโค้ดสปาเก็ตตี้ง่ายเกินไปหรือไม่

## 2. ใช้คอลแบ็ก

อีกวิธีหนึ่งคือส่งคอลแบ็กไปยังคอมโพเนนต์ลูก เช่น `on_click`

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

คุณจะสังเกตว่าในขณะที่ `<ButtonA/>` ได้รับ `WriteSignal` และตัดสินใจเองว่าจะแก้ไขมันอย่างไร
`<ButtonB/>` เพียงแค่ยิงเหตุการณ์ออกไป โดยการแก้ไขเกิดขึ้นที่ `<App/>` นั่นเอง วิธีนี้มีข้อดี
คือทำให้สถานะภายในคงอยู่ภายใน ป้องกันปัญหาการแก้ไขแบบสปาเก็ตตี้ แต่ก็หมายความว่า
โลจิกในการแก้ไขสัญญาณนั้นต้องอยู่ที่ `<App/>` ด้านบน ไม่ใช่ที่ `<ButtonB/>` ด้านล่าง
สิ่งเหล่านี้คือข้อแลกเปลี่ยนจริง ไม่ใช่ตัวเลือกระหว่างถูกกับผิดแบบง่ายๆ

## 3. ใช้ตัวรับฟังเหตุการณ์

อันที่จริงคุณเขียนตัวเลือกที่ 2 ด้วยวิธีที่ต่างออกไปเล็กน้อยได้ ถ้าคอลแบ็กนั้นแมปโดยตรง
เข้ากับอีเวนต์ DOM แบบเนทีฟ คุณสามารถเพิ่มตัวรับฟัง `on:` ลงไปตรงจุดที่คุณใช้
คอมโพเนนต์ในมาโคร `view` ใน `<App/>` ได้เลย

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

วิธีนี้ช่วยให้คุณเขียนโค้ดใน `<ButtonC/>` ได้น้อยกว่าที่เขียนใน `<ButtonB/>` มาก
และยังมอบอีเวนต์ที่มีชนิดถูกต้องให้กับตัวรับฟังด้วย กลไกนี้ทำงานโดยเพิ่ม
ตัวรับฟังอีเวนต์ `on:` ให้กับทุกเอลิเมนต์ที่ `<ButtonC/>` คืนค่า ซึ่งในกรณีนี้
ก็มีเพียง `<button>` ตัวเดียว

แน่นอนว่าวิธีนี้ใช้ได้เฉพาะกับอีเวนต์ DOM จริงที่คุณส่งผ่านตรงไป
ยังเอลิเมนต์ที่คุณเรนเดอร์ในคอมโพเนนต์เท่านั้น สำหรับโลจิกที่ซับซ้อนกว่า
ซึ่งไม่ได้แมปโดยตรงเข้ากับเอลิเมนต์ (เช่น คุณสร้าง `<ValidatedForm/>` แล้วต้องการ
คอลแบ็ก `on_valid_form_submit`) คุณควรใช้ตัวเลือกที่ 2

## 4. การให้คอนเท็กซ์

เวอร์ชันนี้จริงๆ แล้วเป็นรูปแบบย่อยของตัวเลือกที่ 1 สมมติว่าคุณมีแผนผัง
คอมโพเนนต์ที่ซ้อนกันลึก:

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

ตอนนี้ `<ButtonD/>` ไม่ใช่ลูกโดยตรงของ `<App/>` อีกต่อไป คุณจึงไม่สามารถ
ส่ง `WriteSignal` ให้พร็อพของมันได้ง่ายๆ คุณอาจทำสิ่งที่บางครั้งเรียกว่า
“prop drilling” โดยเพิ่มพร็อพให้กับทุกชั้นระหว่างทั้งสอง:

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

แบบนี้ยุ่งเหยิงไปหมด `<Layout/>` กับ `<Content/>` ไม่ได้ต้องการ `set_toggled` เลย
แค่ส่งต่อมันไปให้ `<ButtonD/>` เท่านั้น แต่เราต้องประกาศพร็อพซ้ำถึงสามที่
ซึ่งไม่เพียงน่ารำคาญแต่ยังบำรุงรักษายากด้วย: ลองจินตนาการว่าเราเพิ่มตัวเลือก “half-toggled”
แล้วชนิดของ `set_toggled` ต้องเปลี่ยนเป็น `enum` เราก็ต้องแก้
มันถึงสามที่!

ไม่มีวิธีที่จะข้ามชั้นไปได้เลยหรือ?

มีสิ!

### 4.1 คอนเท็กซ์ API

คุณสามารถให้ข้อมูลที่ข้ามชั้นได้โดยใช้ [`provide_context`](https://docs.rs/leptos/latest/leptos/context/fn.provide_context.html)
และ [`use_context`](https://docs.rs/leptos/latest/leptos/context/fn.use_context.html) คอนเท็กซ์ถูกระบุ
ด้วยชนิดของข้อมูลที่คุณให้ (ในตัวอย่างนี้คือ `WriteSignal<bool>`) และมันอยู่ในแผนผัง
จากบนลงล่างที่ไล่ตามโครงร่างของแผนผัง UI ของคุณ ในตัวอย่างนี้ เราใช้คอนเท็กซ์เพื่อข้าม
การส่งพร็อพไล่ลงไปทุกชั้นที่ไม่จำเป็นได้

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

ข้อควรระวังเดียวกันกับ `<ButtonA/>` ก็ใช้กับวิธีนี้ด้วย: การส่ง `WriteSignal`
ไปทั่วควรทำอย่างระมัดระวัง เพราะมันเปิดทางให้คุณแก้ไขสถานะจาก
ส่วนใดก็ได้ของโค้ด แต่ถ้าทำอย่างรอบคอบแล้ว นี่อาจเป็นหนึ่งใน
เทคนิคที่มีประสิทธิผลที่สุดสำหรับการจัดการสถานะส่วนกลางใน Leptos: เพียง
ให้สถานะที่ระดับสูงสุดที่คุณจะต้องใช้ แล้วนำไปใช้ตรงจุดที่
คุณต้องการด้านล่าง

โปรดทราบว่าวิธีนี้ไม่มีข้อเสียด้านประสิทธิภาพ เพราะคุณ
กำลังส่งสัญญาณรีแอกทีฟแบบละเอียด _จะไม่มีอะไรเกิดขึ้น_ ในคอมโพเนนต์
ที่อยู่คั่นกลาง (`<Layout/>` และ `<Content/>`) เมื่อคุณอัปเดตมัน คุณกำลังสื่อสาร
กันโดยตรงระหว่าง `<ButtonD/>` กับ `<App/>` อันที่จริง และนี่คือพลังของ
รีแอกทิวิตีแบบละเอียด คุณกำลังสื่อสารกันโดยตรงระหว่างการคลิกปุ่ม
ใน `<ButtonD/>` กับโหนดข้อความโหนดเดียวใน `<App/>` ราวกับว่าคอมโพเนนต์
เหล่านั้นไม่มีอยู่เลย และก็... ในขณะรัน มันไม่มีอยู่จริง มีเพียง
สัญญาณและเอฟเฟกต์ ไล่ลงไปจนถึงชั้นล่างสุด

โปรดทราบว่าวิธีนี้มีข้อแลกเปลี่ยนสำคัญ: คุณไม่มีความปลอดภัยของชนิดข้อมูล
ระหว่าง `provide_context` กับ `use_context` อีกต่อไป การได้รับคอนเท็กซ์ที่ถูกต้อง
ในคอมโพเนนต์ลูกเป็นการตรวจสอบขณะรัน (ดู `use_context.expect(...)`) ส่วน
คอมไพเลอร์จะไม่นำทางคุณระหว่างการรีแฟกเตอร์ เหมือนที่มันทำกับวิธีแรกๆ

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/8-parent-child-0-7-cgcgk9?file=%2Fsrc%2Fmain.rs%3A1%2C1-116%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

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
