# การจัดการข้อผิดพลาด

[ในบทที่แล้ว](./06_control_flow.md) เราได้เห็นกันแล้วว่าเราสามารถเรนเดอร์ `Option<T>` ได้ โดยในกรณี `None` จะไม่เรนเดอร์อะไรเลย และในกรณี `Some(T)` จะเรนเดอร์ `T` ออกมา (หาก `T` อิมพลีเมนต์ `IntoView`) สำหรับ `Result<T, E>` ก็ทำงานในลักษณะที่คล้ายกันมาก คือในกรณีที่เป็น `Err(_)` จะไม่เรนเดอร์อะไรเลย แต่ถ้าเป็น `Ok(T)` ก็จะเรนเดอร์ `T` ออกมาให้

เรามาเริ่มด้วยคอมโพเนนต์ง่าย ๆ เพื่อรับค่าตัวเลขจากช่องอินพุตกัน

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

ทุกครั้งที่ค่าในอินพุตเปลี่ยนแปลง `on:input` จะพยายามแปลงค่าข้อความเป็นจำนวนเต็ม 32 บิต (`i32`) แล้วเก็บลงในสัญญาณ `value` ซึ่งมีชนิดข้อมูลเป็น `Result<i32, _>` หากคุณพิมพ์ตัวเลข `42` หน้าจอ UI จะแสดงผลว่า

```
You entered 42
```

แต่ถ้าคุณพิมพ์ข้อความเช่น `foo` หน้าจอจะแสดงผลเป็น

```
You entered
```

ซึ่งผลลัพธ์แบบนี้ยังไม่ค่อยดีเท่าไร แม้ว่าจะช่วยให้เราไม่ต้องคอยเรียก `.unwrap_or_default()` ด้วยตัวเอง แต่จะดีกว่ามากหากเราสามารถดักจับข้อผิดพลาด (catch error) แล้วนำมาแสดงผลหรือจัดการอย่างเหมาะสมได้

คุณสามารถทำสิ่งนั้นได้ด้วยคอมโพเนนต์ [`<ErrorBoundary/>`](https://docs.rs/leptos/latest/leptos/error/fn.ErrorBoundary.html)

```admonish note
หลายคนมักคิดว่า `<input type="number">` ช่วยป้องกันไม่ให้พิมพ์ข้อความอย่าง `foo` หรือสิ่งที่ไม่ใช่ตัวเลขได้อยู่แล้ว ซึ่งเรื่องนี้เป็นจริงแค่ในเบราว์เซอร์บางตัวเท่านั้น แต่ไม่ใช่กับทุกตัว! ยิ่งไปกว่านั้น ยังมีค่าอีกหลายอย่างที่สามารถพิมพ์ลงในช่อง input number ทั่วไปได้แต่ไม่ใช่ `i32` เช่น เลขทศนิยม, ตัวเลขที่มีขนาดเกิน 32 บิต, ตัวอักษร `e` (สัญกรณ์วิทยาศาสตร์) เป็นต้น แม้เราจะสามารถตั้งค่าให้เบราว์เซอร์ช่วยตรวจสอบเงื่อนไขบางอย่างได้ แต่พฤติกรรมระหว่างแต่ละเบราว์เซอร์ก็ยังคงแตกต่างกันอยู่ดี การแปลงและตรวจสอบข้อมูลด้วยตัวคุณเองจึงเป็นเรื่องสำคัญเสมอ!
```

## `<ErrorBoundary/>`

`<ErrorBoundary/>` มีลักษณะคล้ายกับคอมโพเนนต์ `<Show/>` ที่เราเห็นในบทที่แล้วอยู่บ้าง หากทุกอย่างเรียบร้อยดี (นั่นคือ หากค่าทั้งหมดเป็น `Ok(_)`) มันจะเรนเดอร์คอมโพเนนต์ลูก (children) ออกมาตามปกติ แต่หากมี `Err(_)` ถูกเรนเดอร์ขึ้นมาภายใน children เหล่านั้น มันจะสลับไปแสดงผล `fallback` ของ `<ErrorBoundary/>` ทันที

เรามาลองใส่ `<ErrorBoundary/>` เข้าไปในตัวอย่างนี้กัน

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

แต่หากคุณพิมพ์ `foo` ค่าของสัญญาณจะเป็น `Err(_)` และ `fallback` จะถูกเรนเดอร์ขึ้นมาแทน ในที่นี้เราเลือกที่จะเรนเดอร์รายการข้อผิดพลาดออกมาเป็นข้อความ `String` คุณจึงจะเห็นข้อความประมาณนี้:

```
Not a number! Errors:
- cannot parse integer from empty string
```

และเมื่อคุณแก้ไขข้อผิดพลาดให้ถูกต้อง ข้อความแจ้งเตือนข้อผิดพลาดก็จะหายไป และเนื้อหาที่คุณครอบไว้ภายใน `<ErrorBoundary/>` ก็จะกลับมาแสดงผลอีกครั้ง

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/7-errors-0-7-qqywqz?file=%2Fsrc%2Fmain.rs%3A5%2C1-46%2C6&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

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
