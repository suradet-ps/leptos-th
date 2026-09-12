# การจัดการข้อผิดพลาด

[ในบทที่แล้ว](./06_control_flow.md) เราได้เห็นว่าคุณสามารถเรนเดอร์ `Option<T>`:
ในกรณี `None` มันจะไม่เรนเดอร์อะไรเลย และในกรณี `Some(T)` มันจะเรนเดอร์ `T`
(นั่นคือ ถ้า `T` อิมพลีเมนต์ `IntoView`) อันที่จริงคุณทำสิ่งที่คล้ายกันมากได้
กับ `Result<T, E>` ในกรณี `Err(_)` มันจะไม่เรนเดอร์อะไรเลย ส่วนในกรณี `Ok(T)`
มันจะเรนเดอร์ `T`

มาเริ่มกันด้วยคอมโพเนนต์ง่ายๆ สำหรับรับข้อมูลตัวเลขจากอินพุต

```rust
#[component]
fn NumericInput() -> impl IntoView {
    let (value, set_value) = signal(Ok(0));

    view! {
        <label>
            "Type an integer (or not!)"
            <input type="number" on:input:target=move |ev| {
              // when input changes, try to parse a number from the input
              set_value.set(ev.target().value().parse::<i32>())
            }/>
            <p>
                "You entered "
                <strong>{value}</strong>
            </p>
        </label>
    }
}
```

ทุกครั้งที่คุณเปลี่ยนค่าอินพุต `on_input` จะพยายามแยกวิเคราะห์ค่าของมันให้เป็นจำนวนเต็ม
32 บิต (`i32`) แล้วเก็บไว้ในสัญญาณ `value` ของเรา ซึ่งเป็น `Result<i32, _>` ถ้าคุณ
พิมพ์เลข `42` UI จะแสดง

```
You entered 42
```

แต่ถ้าคุณพิมพ์สตริง `foo` มันจะแสดง

```
You entered
```

แบบนี้ยังไม่ค่อยดีนัก มันช่วยให้เราไม่ต้องใช้ `.unwrap_or_default()` หรืออะไรทำนองนั้น แต่จะ
ดีกว่ามากถ้าเราจับข้อผิดพลาดและทำอะไรบางอย่างกับมันได้

คุณทำแบบนั้นได้ด้วยคอมโพเนนต์
[`<ErrorBoundary/>`](https://docs.rs/leptos/latest/leptos/error/fn.ErrorBoundary.html)

```admonish note
หลายคนมักพยายามชี้ให้เห็นว่า `<input type="number">` ป้องกันไม่ให้คุณพิมพ์สตริง
อย่าง `foo` หรืออะไรก็ตามที่ไม่ใช่ตัวเลข ซึ่งเรื่องนี้เป็นจริงในเบราว์เซอร์บางตัว แต่ไม่ใช่ทั้งหมด!
ยิ่งไปกว่านั้น ยังมีอีกสารพัดที่พิมพ์ลงในอินพุตตัวเลขธรรมดาได้แต่ไม่ใช่
`i32`: จำนวนทศนิยม ตัวเลขที่ใหญ่กว่า 32 บิต ตัวอักษร `e` และอื่นๆ เบราว์เซอร์
อาจถูกสั่งให้รักษาข้อกำหนดบางอย่างเหล่านี้ไว้ได้ แต่พฤติกรรมของเบราว์เซอร์ก็ยังแตกต่างกัน: การแยกวิเคราะห์
ด้วยตัวคุณเองจึงสำคัญ!
```

## `<ErrorBoundary/>`

`<ErrorBoundary/>` คล้ายกับคอมโพเนนต์ `<Show/>` ที่เราเห็นในบทที่แล้วอยู่เล็กน้อย
ถ้าทุกอย่างเรียบร้อย ซึ่งก็คือถ้าทุกอย่างเป็น `Ok(_)` มันจะเรนเดอร์ลูก (children) ของมัน
แต่ถ้ามี `Err(_)` ถูกเรนเดอร์อยู่ท่ามกลาง children เหล่านั้น มันจะกระตุ้น
`fallback` ของ `<ErrorBoundary/>`

มาเพิ่ม `<ErrorBoundary/>` ลงในตัวอย่างนี้กัน

```rust
#[component]
fn NumericInput() -> impl IntoView {
        let (value, set_value) = signal(Ok(0));

    view! {
        <h1>"Error Handling"</h1>
        <label>
            "Type a number (or something that's not a number!)"
            <input type="number" on:input:target=move |ev| {
                // when input changes, try to parse a number from the input
                set_value.set(ev.target().value().parse::<i32>())
            }/>
            // If an `Err(_) had been rendered inside the <ErrorBoundary/>,
            // the fallback will be displayed. Otherwise, the children of the
            // <ErrorBoundary/> will be displayed.
            <ErrorBoundary
                // the fallback receives a signal containing current errors
                fallback=|errors| view! {
                    <div class="error">
                        <p>"Not a number! Errors: "</p>
                        // we can render a list of errors
                        // as strings, if we'd like
                        <ul>
                            {move || errors.get()
                                .into_iter()
                                .map(|(_, e)| view! { <li>{e.to_string()}</li>})
                                .collect::<Vec<_>>()
                            }
                        </ul>
                    </div>
                }
            >
                <p>
                    "You entered "
                    // because `value` is `Result<i32, _>`,
                    // it will render the `i32` if it is `Ok`,
                    // and render nothing and trigger the error boundary
                    // if it is `Err`. It's a signal, so this will dynamically
                    // update when `value` changes
                    <strong>{value}</strong>
                </p>
            </ErrorBoundary>
        </label>
    }
}
```

ตอนนี้ ถ้าคุณพิมพ์ `42` `value` จะเป็น `Ok(42)` แล้วคุณจะเห็น

```
You entered 42
```

ถ้าคุณพิมพ์ `foo` ค่า value จะเป็น `Err(_)` และ `fallback` จะถูกเรนเดอร์ เราเลือกที่จะเรนเดอร์
รายการข้อผิดพลาดเป็น `String` ดังนั้นคุณจะเห็นอะไรประมาณนี้

```
Not a number! Errors:
- cannot parse integer from empty string
```

ถ้าคุณแก้ไขข้อผิดพลาด ข้อความข้อผิดพลาดจะหายไป และเนื้อหาที่คุณห่อไว้ใน
`<ErrorBoundary/>` จะปรากฏขึ้นอีกครั้ง

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/7-errors-0-7-qqywqz?file=%2Fsrc%2Fmain.rs%3A5%2C1-46%2C6&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/7-errors-0-7-qqywqz?file=%2Fsrc%2Fmain.rs%3A5%2C1-46%2C6&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>
```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (value, set_value) = signal(Ok(0));

    view! {
        <h1>"Error Handling"</h1>
        <label>
            "Type a number (or something that's not a number!)"
            <input type="number" on:input:target=move |ev| {
                // when input changes, try to parse a number from the input
                set_value.set(ev.target().value().parse::<i32>())
            }/>
            // If an `Err(_) had been rendered inside the <ErrorBoundary/>,
            // the fallback will be displayed. Otherwise, the children of the
            // <ErrorBoundary/> will be displayed.
            <ErrorBoundary
                // the fallback receives a signal containing current errors
                fallback=|errors| view! {
                    <div class="error">
                        <p>"Not a number! Errors: "</p>
                        // we can render a list of errors
                        // as strings, if we'd like
                        <ul>
                            {move || errors.get()
                                .into_iter()
                                .map(|(_, e)| view! { <li>{e.to_string()}</li>})
                                .collect::<Vec<_>>()
                            }
                        </ul>
                    </div>
                }
            >
                <p>
                    "You entered "
                    // because `value` is `Result<i32, _>`,
                    // it will render the `i32` if it is `Ok`,
                    // and render nothing and trigger the error boundary
                    // if it is `Err`. It's a signal, so this will dynamically
                    // update when `value` changes
                    <strong>{value}</strong>
                </p>
            </ErrorBoundary>
        </label>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
