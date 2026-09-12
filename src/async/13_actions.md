# การแก้ไขข้อมูลด้วยแอ็กชัน

เราพูดคุยกันไปแล้วเกี่ยวกับวิธีโหลดข้อมูล `async` ด้วยรีซอร์ส รีซอร์สจะโหลดข้อมูลทันที
และทำงานร่วมกับคอมโพเนนต์ `<Suspense/>` และ `<Transition/>` อย่างใกล้ชิดเพื่อแสดงว่า
ข้อมูลกำลังโหลดอยู่ในแอปของคุณหรือไม่ แต่ถ้าคุณเพียงต้องการเรียกฟังก์ชัน `async`
อะไรก็ตามและติดตามว่ามันกำลังทำอะไรอยู่ล่ะ?

คือ คุณใช้ [`spawn_local`](https://docs.rs/leptos/latest/leptos/task/fn.spawn_local.html)
ได้เสมอ วิธีนี้ช่วยให้คุณสปอว์นงาน `async` ในสภาพแวดล้อมแบบซิงโครนัสได้โดยส่ง `Future`
ต่อไปให้เบราว์เซอร์ (หรือบนเซิร์ฟเวอร์ ก็เป็น Tokio หรือรันไทม์อื่นที่คุณใช้อยู่)
แต่คุณจะรู้ได้อย่างไรว่ามันยังรอดำเนินการอยู่? คุณก็แค่ตั้งสัญญาณตัวหนึ่งเพื่อแสดงว่า
กำลังโหลด และอีกตัวเพื่อแสดงผลลัพธ์...

ทั้งหมดนั้นก็ถูกต้อง หรือคุณจะใช้พริดิมิตีฟ `async` ตัวสุดท้ายก็ได้:
[`Action`](https://docs.rs/leptos/latest/leptos/reactive/actions/struct.Action.html)

แอ็กชันและรีซอร์สดูคล้ายกัน แต่พวกมันเป็นตัวแทนของสิ่งพื้นฐานที่แตกต่างกัน หากคุณ
กำลังพยายามโหลดข้อมูลด้วยการรันฟังก์ชัน `async` ไม่ว่าจะครั้งเดียวหรือเมื่อค่าอื่น
เปลี่ยนแปลง คุณน่าจะต้องการใช้รีซอร์ส หากคุณกำลังพยายามรันฟังก์ชัน `async` เป็นครั้งคราว
เพื่อตอบสนองต่อบางอย่าง เช่น ผู้ใช้คลิกปุ่ม คุณน่าจะต้องการใช้ `Action`

สมมติว่าเรามีฟังก์ชัน `async` ที่ต้องการรัน

```rust
async fn add_todo_request(new_title: &str) -> Uuid {
    /* do some stuff on the server to add a new todo */
}
```

`Action::new()` รับฟังก์ชัน `async` ที่รับรีเฟอเรนซ์ไปยังอาร์กิวเมนต์ตัวเดียว
ซึ่งคุณอาจคิดว่ามันคือ “ชนิดอินพุต” ของมัน

> อินพุตเป็นชนิดเดียวเสมอ หากคุณต้องการส่งอาร์กิวเมนต์หลายตัว ก็ทำได้ด้วยสตรักต์หรือทูเพิล
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
> เพราะฟังก์ชันของแอ็กชันรับรีเฟอเรนซ์ แต่ `Future` จำเป็นต้องมีไลฟ์ไทม์ `'static` คุณจึงมักต้องโคลนค่าเพื่อส่งเข้าไปใน `Future` ซึ่งต้องยอมรับว่าดูไม่สวยงามสักหน่อย แต่มันปลดล็อกฟีเจอร์อันทรงพลังอย่าง optimistic UI เราจะเห็นรายละเอียดเพิ่มเติมเกี่ยวกับเรื่องนี้ในบทต่อๆ ไป

ดังนั้นในกรณีนี้ สิ่งที่เราต้องทำเพื่อสร้างแอ็กชันก็แค่

```rust
let add_todo_action = Action::new(|input: &String| {
    let input = input.to_owned();
    async move { add_todo_request(&input).await }
});
```

แทนที่จะเรียก `add_todo_action` โดยตรง เราจะเรียกมันผ่าน `.dispatch()` ดังนี้

```rust
add_todo_action.dispatch("Some value".to_string());
```

คุณสามารถทำสิ่งนี้ได้จากตัวรับฟังเหตุการณ์ จากตัวจับเวลา หรือจากที่ไหนก็ได้
เพราะ `.dispatch()` ไม่ใช่ฟังก์ชัน `async` มันจึงเรียกได้จากบริบทแบบซิงโครนัส

แอ็กชันให้การเข้าถึงสัญญาณสองสามตัวที่ซิงโครไนซ์ระหว่างแอ็กชันอะซิงโครนัสที่คุณกำลังเรียก
กับระบบรีแอกทีฟแบบซิงโครนัส:

```rust
let submitted = add_todo_action.input(); // RwSignal<Option<String>>
let pending = add_todo_action.pending(); // ReadSignal<bool>
let todo_id = add_todo_action.value(); // RwSignal<Option<Uuid>>
```

สิ่งนี้ทำให้การติดตามสถานะปัจจุบันของคำขอ การแสดงตัวบ่งชี้การโหลด หรือการทำ
optimistic UI บนสมมติฐานว่าการส่งจะสำเร็จ เป็นเรื่องง่าย

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

ตอนนี้ อาจมีโอกาสที่ทั้งหมดนี้ดูซับซ้อนเกินไป หรืออาจดูจำกัดเกินไป ผมอยากรวมแอ็กชัน
ไว้ตรงนี้ คู่กับรีซอร์ส ในฐานะชิ้นส่วนที่หายไปของภาพรวม ในแอป Leptos จริงๆ คุณมักจะใช้
แอ็กชันร่วมกับฟังก์ชันฝั่งเซิร์ฟเวอร์ [`ServerAction`](https://docs.rs/leptos/latest/leptos/server/struct.ServerAction.html)
และคอมโพเนนต์ [`<ActionForm/>`](https://docs.rs/leptos/latest/leptos/form/fn.ActionForm.html)
เพื่อสร้างฟอร์มที่เสริมความสามารถแบบก้าวหน้าอันทรงพลัง ดังนั้นหากพริดิมิตีฟนี้ดูไม่มี
ประโยชน์สำหรับคุณ... ไม่ต้องกังวล! บางทีมันอาจเข้าใจได้ในภายหลัง (หรือลองดูตัวอย่าง
[`todo_app_sqlite`](https://github.com/leptos-rs/leptos/blob/main/examples/todo_app_sqlite/src/todo.rs)
ของเราตอนนี้เลยก็ได้)

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
