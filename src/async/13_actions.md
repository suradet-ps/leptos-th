# การแก้ไขข้อมูลด้วยแอ็กชัน

เราได้คุยกันไปแล้วเกี่ยวกับวิธีโหลดข้อมูล `async` ด้วยรีซอร์ส ซึ่งรีซอร์สจะเริ่มโหลดข้อมูลทันที และทำงานร่วมกับคอมโพเนนต์ `<Suspense/>` และ `<Transition/>` อย่างใกล้ชิดเพื่อแสดงสถานะว่าข้อมูลกำลังโหลดอยู่ในแอปพลิเคชันของคุณหรือไม่ แต่ถ้าหากคุณเพียงต้องการเรียกฟังก์ชัน `async` ทั่วไป และคอยติดตามว่ามันกำลังดำเนินการถึงไหนแล้วล่ะ?

แน่นอนว่าคุณสามารถใช้ [`spawn_local`](https://docs.rs/leptos/latest/leptos/task/fn.spawn_local.html) ได้เสมอ ซึ่งวิธีนี้ช่วยให้คุณสามารถสปอว์นงาน `async` ขึ้นมาทำงานในสภาพแวดล้อมแบบซิงโครนัสได้ โดยการส่งมอบ `Future` ให้เบราว์เซอร์ (หรือบนเซิร์ฟเวอร์ก็คือ Tokio หรือรันไทม์ตัวอื่นที่คุณเลือกใช้) นำไปจัดการ แต่คุณจะรู้ได้อย่างไรว่างานนั้นยังคงรอดำเนินการ (pending) อยู่หรือไม่? คุณอาจจะต้องสร้างสัญญาณตัวหนึ่งขึ้นมาเพื่อเก็บสถานะกำลังโหลด และสร้างอีกตัวหนึ่งขึ้นมาเพื่อเก็บผลลัพธ์...

แนวทางดังกล่าวก็ถูกต้องทั้งหมด หรือคุณจะเลือกใช้พริมิทีฟ `async` ตัวสุดท้ายนี้ก็ได้ นั่นคือ: [`Action`](https://docs.rs/leptos/latest/leptos/reactive/actions/struct.Action.html)

แอ็กชัน (Action) และรีซอร์ส (Resource) อาจดูคล้ายกัน แต่จริง ๆ แล้วเป็นตัวแทนของแนวคิดพื้นฐานที่ต่างกันอย่างสิ้นเชิง: หากคุณต้องการโหลดข้อมูลด้วยการรันฟังก์ชัน `async` ไม่ว่าจะเป็นการโหลดเพียงครั้งเดียว หรือโหลดซ้ำเมื่อมีค่าอื่นเปลี่ยนแปลง คุณควรเลือกใช้รีซอร์ส แต่หากคุณต้องการรันฟังก์ชัน `async` เป็นครั้งคราวเพื่อตอบสนองต่อเหตุการณ์บางอย่าง เช่น การที่ผู้ใช้คลิกปุ่ม คุณควรเลือกใช้ `Action`

สมมติว่าเรามีฟังก์ชัน `async` ที่ต้องการสั่งรันดังนี้:

```rust
async fn add_todo_request(new_title: &str) -> Uuid {
    /* do some stuff on the server to add a new todo */
}
```

`Action::new()` จะรับฟังก์ชัน `async` ที่รับการอ้างอิง (reference) ไปยังอาร์กิวเมนต์ตัวเดียว ซึ่งคุณอาจมองว่านั่นคือ "ชนิดข้อมูลอินพุต" (input type) ของมัน

> อินพุตจะเป็นชนิดข้อมูลตัวเดียวเสมอ หากคุณต้องการส่งอาร์กิวเมนต์หลายตัว ก็สามารถทำได้โดยการใช้สตรัคต์หรือทูเพิล (tuple)
>
> ```rust
> // if there's a single argument, just use that
> let action1 = Action::new(|input: &String| {
>    let input = input.clone();
>    async move { todo!() }
> });
>
> // if there are no arguments, use the unit type `()`
> let action2 = Action::new(|input: &()| async { todo!() });
>
> // if there are multiple arguments, use a tuple
> let action3 = Action::new(
>   |input: &(usize, String)| async { todo!() }
> );
> ```
>
> เนื่องจากฟังก์ชันของแอ็กชันรับค่ามาเป็นการอ้างอิง (reference) แต่ `Future` จำเป็นต้องมีไลฟ์ไทม์แบบ `'static` คุณจึงมักต้องโคลนค่าเพื่อย้าย (move) เข้าไปใน `Future` ซึ่งต้องยอมรับว่าอาจดูไม่ค่อยสะดวกนัก แต่มันช่วยปลดล็อกฟีเจอร์อันทรงพลังอย่าง optimistic UI ได้ เราจะได้เห็นรายละเอียดเพิ่มเติมเกี่ยวกับเรื่องนี้ในบทต่อ ๆ ไป

ดังนั้นในกรณีนี้ สิ่งที่เราต้องทำเพื่อสร้างแอ็กชันก็มีเพียงแค่นี้:

```rust
let add_todo_action = Action::new(|input: &String| {
    let input = input.to_owned();
    async move { add_todo_request(&input).await }
});
```

แทนที่จะเรียกใช้งาน `add_todo_action` โดยตรง เราจะสั่งรันมันผ่านเมธอด `.dispatch()` ดังนี้:

```rust
add_todo_action.dispatch("Some value".to_string());
```

คุณสามารถเรียกเมธอดนี้ได้จากตัวรับฟังเหตุการณ์ (event listener), ตัวจับเวลา หรือจากที่ใดก็ได้ เพราะ `.dispatch()` ไม่ใช่ฟังก์ชัน `async` จึงสามารถเรียกใช้จากบริบทที่เป็นซิงโครนัสได้อย่างสมบูรณ์

แอ็กชันเปิดให้เราเข้าถึงสัญญาณหลายตัว ซึ่งทำหน้าที่ซิงโครไนซ์ระหว่างแอ็กชันแบบอะซิงโครนัสที่คุณเรียก กับระบบรีแอกทีฟที่เป็นแบบซิงโครนัส:

```rust
let submitted = add_todo_action.input(); // RwSignal<Option<String>>
let pending = add_todo_action.pending(); // ReadSignal<bool>
let todo_id = add_todo_action.value(); // RwSignal<Option<Uuid>>
```

สิ่งนี้ช่วยให้คุณติดตามสถานะปัจจุบันของคำขอ, แสดงตัวบ่งชี้สถานะการโหลด หรือทำ optimistic UI (การอัปเดต UI ทันทีล่วงหน้าบนสมมติฐานว่าคำขอจะสำเร็จ) ได้อย่างง่ายดาย

```rust
let input_ref = NodeRef::<Input>::new();

view! {
    <form
        on:submit=move |ev| {
            ev.prevent_default(); // don't reload the page...
            let input = input_ref.get().expect("input to exist");
            add_todo_action.dispatch(input.value());
        }
    >
        <label>
            "What do you need to do?"
            <input type="text"
                node_ref=input_ref
            />
        </label>
        <button type="submit">"Add Todo"</button>
    </form>
    // use our loading state
    <p>{move || pending.get().then_some("Loading...")}</p>
}
```

ตอนนี้ อาจมีโอกาสที่คุณจะรู้สึกว่าทั้งหมดนี้ดูซับซ้อนเกินไป หรืออาจดูจำกัดเกินไป แต่เราต้องการนำเสนอแอ็กชันไว้ที่นี่คู่กับรีซอร์ส เพื่อเติมเต็มชิ้นส่วนสำคัญของภาพรวมให้สมบูรณ์ ในการพัฒนาแอปพลิเคชัน Leptos จริง ๆ บ่อยครั้งคุณจะใช้แอ็กชันควบคู่ไปกับฟังก์ชันฝั่งเซิร์ฟเวอร์ [`ServerAction`](https://docs.rs/leptos/latest/leptos/server/struct.ServerAction.html) และคอมโพเนนต์ [`<ActionForm/>`](https://docs.rs/leptos/latest/leptos/form/fn.ActionForm.html) เพื่อสร้างแบบฟอร์มที่รองรับการเพิ่มประสิทธิภาพแบบก้าวหน้า (progressive enhancement) ได้อย่างทรงพลัง ดังนั้นหากพริมิทีฟตัวนี้ยังดูเหมือนไม่ค่อยมีประโยชน์สำหรับคุณในตอนนี้... ไม่ต้องกังวล! เมื่อเรียนรู้ต่อไปในภายหลัง คุณจะเข้าใจบทบาทของมันได้ชัดเจนขึ้น (หรือจะลองเข้าไปดูตัวอย่าง [`todo_app_sqlite`](https://github.com/leptos-rs/leptos/blob/main/examples/todo_app_sqlite/src/todo.rs) ของเราในตอนนี้เลยก็ได้)

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/13-action-0-7-g73rl9?file=%2Fsrc%2Fmain.rs)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/13-action-0-7-g73rl9?file=%2Fsrc%2Fmain.rs" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use gloo_timers::future::TimeoutFuture;
use leptos::{html::Input, prelude::*};
use uuid::Uuid;

// Here we define an async function
// This could be anything: a network request, database read, etc.
// Think of it as a mutation: some imperative async action you run,
// whereas a resource would be some async data you load
async fn add_todo(text: &str) -> Uuid {
    _ = text;
    // fake a one-second delay
    // SendWrapper allows us to use this !Send browser API; don't worry about it
    send_wrapper::SendWrapper::new(TimeoutFuture::new(1_000)).await;
    // pretend this is a post ID or something
    Uuid::new_v4()
}

#[component]
pub fn App() -> impl IntoView {
    // an action takes an async function with single argument
    // it can be a simple type, a struct, or ()
    let add_todo = Action::new(|input: &String| {
        // the input is a reference, but we need the Future to own it
        // this is important: we need to clone and move into the Future
        // so it has a 'static lifetime
        let input = input.to_owned();
        async move { add_todo(&input).await }
    });

    // actions provide a bunch of synchronous, reactive variables
    // that tell us different things about the state of the action
    let submitted = add_todo.input();
    let pending = add_todo.pending();
    let todo_id = add_todo.value();

    let input_ref = NodeRef::<Input>::new();

    view! {
        <form
            on:submit=move |ev| {
                ev.prevent_default(); // don't reload the page...
                let input = input_ref.get().expect("input to exist");
                add_todo.dispatch(input.value());
            }
        >
            <label>
                "What do you need to do?"
                <input type="text"
                    node_ref=input_ref
                />
            </label>
            <button type="submit">"Add Todo"</button>
        </form>
        <p>{move || pending.get().then_some("Loading...")}</p>
        <p>
            "Submitted: "
            <code>{move || format!("{:#?}", submitted.get())}</code>
        </p>
        <p>
            "Pending: "
            <code>{move || format!("{:#?}", pending.get())}</code>
        </p>
        <p>
            "Todo ID: "
            <code>{move || format!("{:#?}", todo_id.get())}</code>
        </p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
