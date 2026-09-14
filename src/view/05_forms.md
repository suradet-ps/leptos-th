# ฟอร์มและอินพุต

แบบฟอร์ม (forms) และช่องกรอกข้อมูล (inputs) ถือเป็นหัวใจสำคัญของเว็บแอปพลิเคชันที่มีการโต้ตอบกับผู้ใช้ ใน Leptos มีสองรูปแบบหลักในการจัดการกับอินพุต ซึ่งหากคุณเคยใช้งาน React, SolidJS หรือเฟรมเวิร์กใกล้เคียงมาก่อนก็น่าจะคุ้นเคยกันดี นั่นคือ อินพุตแบบควบคุมโดยเฟรมเวิร์ก (**controlled inputs**) และอินพุตแบบปล่อยให้เบราว์เซอร์ควบคุม (**uncontrolled inputs**)

## อินพุตแบบควบคุม (controlled inputs)

ในรูปแบบ “อินพุตแบบควบคุม” เฟรมเวิร์กจะเป็นผู้ควบคุมสถานะของเอลิเมนต์อินพุตอย่างเบ็ดเสร็จ ทุกครั้งที่เกิดอีเวนต์ `input` ขึ้น โค้ดจะเข้าไปอัปเดตสัญญาณ (signal) ที่เก็บสถานะปัจจุบัน และสัญญาณนั้นก็จะส่งค่ากลับมาอัปเดตพร็อพเพอร์ตี `value` ของช่องอินพุตใน DOM ทันที

มี 2 ข้อสังเกตสำคัญที่ควรทราบ:

1. อีเวนต์ `input` จะถูกทริกเกอร์แทบจะทุกครั้งที่ตัวอักษรในอินพุตเปลี่ยน ส่วนอีเวนต์ `change` มักจะถูกทริกเกอร์เมื่อผู้ใช้เลื่อนโฟกัส (blur) ออกจากช่องอินพุตแล้ว ในกรณีส่วนใหญ่คุณมักจะต้องการใช้ `on:input` แต่ Leptos ก็ให้อิสระแก่คุณในการเลือกใช้ตามต้องการ
2. *แอตทริบิวต์ (attribute)* `value` ใน HTML ทำหน้าที่กำหนดเพียงแค่ค่าเริ่มต้น (initial value) ของช่องอินพุตเท่านั้น นั่นคือมันจะเปลี่ยนค่าบนหน้าจอจนถึงจุดที่ผู้ใช้เริ่มพิมพ์ข้อความลงไป หลังจากนั้น การเปลี่ยนแปลงค่าบนหน้าจอจะต้องทำผ่าน *พร็อพเพอร์ตี (property)* `value` ของ DOM แทน ด้วยเหตุนี้ คุณจึงควรผูกค่าด้วย `prop:value` เสมอ (เช่นเดียวกับการใช้ `prop:checked` แทน `checked` บน `<input type="checkbox">`)

```rust
let (name, set_name) = signal("Controlled".to_string());

view! {
    <input type="text"
        // adding :target gives us typed access to the element
        // that is the target of the event that fires
        on:input:target=move |ev| {
            // .value() returns the current value of an HTML input element
            set_name.set(ev.target().value());
        }

        // the `prop:` syntax lets you update a DOM property,
        // rather than an attribute.
        prop:value=name
    />
    <p>"Name is: " {name}</p>
}
```

> #### ทำไมคุณจึงต้องใช้ `prop:value`?
>
> เว็บเบราว์เซอร์เป็นแพลตฟอร์มที่แพร่หลายและเสถียรที่สุดในโลกสำหรับการเรนเดอร์ส่วนติดต่อผู้ใช้แบบกราฟิก พวกมันยังรักษาความเข้ากันได้ย้อนหลัง (backward compatibility) ได้อย่างน่าทึ่งตลอดสามทศวรรษที่ผ่านมา ดังนั้นจึงเลี่ยงไม่ได้ที่จะมีพฤติกรรมแปลก ๆ ทางประวัติศาสตร์หลงเหลืออยู่บ้าง
>
> ความแปลกอย่างหนึ่งก็คือ ความแตกต่างระหว่างแอตทริบิวต์ของ HTML กับพร็อพเพอร์ตีของเอลิเมนต์ DOM: โดย “แอตทริบิวต์” คือสิ่งที่ถูกพาร์สจาก HTML และสามารถกำหนดบนเอลิเมนต์ DOM ได้ด้วย `.setAttribute()` ส่วน “พร็อพเพอร์ตี” คือฟิลด์ของคลาส JavaScript ที่เป็นตัวแทนของเอลิเมนต์ HTML ที่ถูกพาร์สนั้น
>
> ในกรณีของ `<input value=...>` การกำหนด *แอตทริบิวต์* `value` ถูกนิยามว่าเป็นการกำหนดค่าเริ่มต้นให้อินพุต ส่วนการกำหนด *พร็อพเพอร์ตี* `value` จะกำหนดค่าปัจจุบันของมัน คุณอาจเข้าใจเรื่องนี้ง่ายขึ้นโดยเปิด `about:blank` แล้วรัน JavaScript ต่อไปนี้ในคอนโซลของเบราว์เซอร์ทีละบรรทัด:
>
> ```js
> // create an input and append it to the DOM
> const el = document.createElement("input");
> document.body.appendChild(el);
>
> el.setAttribute("value", "test"); // updates the input
> el.setAttribute("value", "another test"); // updates the input again
>
> // now go and type into the input: delete some characters, etc.
>
> el.setAttribute("value", "one more time?");
> // nothing should have changed. Setting the "initial value" does nothing now
>
> // however...
> el.value = "But this works";
> ```
>
> เฟรมเวิร์กฟรอนต์เอนด์อื่น ๆ หลายตัวปนกันระหว่างแอตทริบิวต์กับพร็อพเพอร์ตี หรือสร้างกรณีพิเศษสำหรับอินพุตเพื่อกำหนดค่าให้ถูกต้อง บางที Leptos ก็ควรทำแบบนั้นเหมือนกัน แต่สำหรับตอนนี้ เราอยากให้ผู้ใช้ควบคุมได้มากที่สุดว่ากำลังกำหนดแอตทริบิวต์หรือพร็อพเพอร์ตี และพยายามให้ความรู้เกี่ยวกับพฤติกรรมจริงของเบราว์เซอร์แทนที่จะปิดบังมันไว้

### ทำให้อินพุตแบบควบคุมง่ายขึ้นด้วย `bind:`

การยึดตามมาตรฐานเว็บและการแบ่งแยกที่ชัดเจนระหว่าง "การอ่านจากสัญญาณ" กับ "การเขียนลงสัญญาณ" นั้นเป็นสิ่งที่ดี แต่การสร้างอินพุตแบบควบคุมด้วยวิธีนี้บางครั้งอาจดูมีโค้ด boilerplate มากเกินจำเป็น

Leptos จึงมีไวยากรณ์ `bind:` พิเศษสำหรับอินพุต ที่ช่วยให้คุณผูกสัญญาณเข้ากับอินพุตได้โดยอัตโนมัติ มันทำสิ่งเดียวกันกับรูปแบบ "อินพุตแบบควบคุม" ข้างต้นทุกประการ คือสร้างตัวรับฟังเหตุการณ์ที่คอยอัปเดตสัญญาณ และผูกพร็อพเพอร์ตีแบบไดนามิกที่อ่านค่าจากสัญญาณ คุณสามารถใช้ `bind:value` กับอินพุตข้อความ, `bind:checked` กับเช็กบ็อกซ์ และ `bind:group` กับกลุ่มปุ่มตัวเลือก (radio button) ได้อย่างสะดวก

```rust
let (name, set_name) = signal("Controlled".to_string());
let email = RwSignal::new("".to_string());
let favorite_color = RwSignal::new("red".to_string());
let spam_me = RwSignal::new(true);

view! {
    <input type="text"
        bind:value=(name, set_name)
    />
    <input type="email"
        bind:value=email
    />
    <label>
        "Please send me lots of spam email."
        <input type="checkbox"
            bind:checked=spam_me
        />
    </label>
    <fieldset>
        <legend>"Favorite color"</legend>
        <label>
            "Red"
            <input
                type="radio"
                name="color"
                value="red"
                bind:group=favorite_color
            />
        </label>
        <label>
            "Green"
            <input
                type="radio"
                name="color"
                value="green"
                bind:group=favorite_color
            />
        </label>
        <label>
            "Blue"
            <input
                type="radio"
                name="color"
                value="blue"
                bind:group=favorite_color
            />
        </label>
    </fieldset>
    <p>"Your favorite color is " {favorite_color} "."</p>
    <p>"Name is: " {name}</p>
    <p>"Email is: " {email}</p>
    <Show when=move || spam_me.get()>
        <p>"You’ll receive cool bonus content!"</p>
    </Show>
}
```

## อินพุตแบบไม่ควบคุม (uncontrolled inputs)

ใน "อินพุตแบบไม่ควบคุม" เบราว์เซอร์จะเป็นผู้ดูแลและควบคุมสถานะของเอลิเมนต์อินพุตเอง แทนที่เราจะต้องคอยอัปเดตสัญญาณรีแอกทีฟทุกครั้งที่พิมพ์ เราจะหันมาใช้ [`NodeRef`](https://docs.rs/leptos/latest/leptos/tachys/reactive_graph/node_ref/struct.NodeRef.html) เพื่อเข้าถึงเอลิเมนต์อินพุตโดยตรงเมื่อถึงเวลาที่เราต้องการอ่านค่า

ในตัวอย่างนี้ เราจะอ่านค่าและแจ้งให้เฟรมเวิร์กทราบเฉพาะตอนที่ `<form>` เกิดเหตุการณ์ `submit` เท่านั้น สังเกตการใช้โมดูล [`leptos::html`](https://docs.rs/leptos/latest/leptos/html/index.html) ซึ่งเตรียมชนิดข้อมูลเฉพาะสำหรับเอลิเมนต์ HTML ทุกตัวไว้ให้ครบครัน

```rust
let (name, set_name) = signal("Uncontrolled".to_string());

let input_element: NodeRef<html::Input> = NodeRef::new();

view! {
    <form on:submit=on_submit> // on_submit defined below
        <input type="text"
            value=name
            node_ref=input_element
        />
        <input type="submit" value="Submit"/>
    </form>
    <p>"Name is: " {name}</p>
}
```

วิวนี้คงอธิบายตัวเองได้ค่อนข้างชัดเจนอยู่แล้ว ณ จุดนี้ ขอให้สังเกตสองเรื่อง:

1. ต่างจากตัวอย่างอินพุตแบบควบคุม ตรงนี้เราใช้ `value` ธรรมดา (ไม่ใช่ `prop:value`) เพราะเรากำหนดแค่ค่าเริ่มต้นของอินพุต แล้วปล่อยให้เบราว์เซอร์ควบคุมสถานะของมันเอง (เราจะใช้ `prop:value` แทนก็ได้)
2. เราใช้ `node_ref=...` เพื่อผูกเอลิเมนต์เข้ากับ `NodeRef` (ในตัวอย่างรุ่นเก่าอาจพบการใช้ `_ref` ซึ่งทำงานเหมือนกัน แต่ `node_ref` ได้รับการสนับสนุนจาก rust-analyzer ที่ดีกว่า)

`NodeRef` เป็นสมาร์ตพอยน์เตอร์แบบรีแอกทีฟชนิดหนึ่ง เราใช้มันเพื่อเข้าถึงโหนด DOM ที่อยู่ข้างใต้ โดยค่าของมันจะถูกกำหนดเมื่อเอลิเมนต์ถูกเรนเดอร์และเมานต์เข้าสู่หน้าเว็บ

```rust
let on_submit = move |ev: SubmitEvent| {
    // stop the page from reloading!
    ev.prevent_default();

    // here, we'll extract the value from the input
    let value = input_element
        .get()
        // event handlers can only fire after the view
        // is mounted to the DOM, so the `NodeRef` will be `Some`
        .expect("<input> should be mounted")
        // `leptos::HtmlElement<html::Input>` implements `Deref`
        // to a `web_sys::HtmlInputElement`.
        // this means we can call`HtmlInputElement::value()`
        // to get the current value of the input
        .value();
    set_name.set(value);
};
```

ตัวจัดการเหตุการณ์ `on_submit` จะเข้าถึงค่าของอินพุตแล้วนำไปอัปเดตผ่าน `set_name.set()` ในการเข้าถึงโหนด DOM ที่เก็บอยู่ใน `NodeRef` เราสามารถเรียกใช้แบบฟังก์ชันได้เลย (หรือเรียก `.get()`) ซึ่งจะคืนค่าเป็น `Option<leptos::HtmlElement<html::Input>>` แต่เนื่องจากเรารู้อยู่แล้วว่าเอลิเมนต์ถูกเมานต์ลงบน DOM เรียบร้อย (ไม่อย่างนั้นผู้ใช้คงกด submit ไม่ได้!) จึงปลอดภัยที่จะ unwrap หรือใช้ `.expect()` ตรงนี้

จากนั้นเราก็เรียก `.value()` เพื่อดึงข้อความออกจากอินพุตได้ทันที เพราะ `NodeRef` มอบการเข้าถึงเอลิเมนต์ HTML พร้อมชนิดข้อมูลที่ถูกต้องแม่นยำ

ลองอ่านเพิ่มเติมได้ที่ [`web_sys` และ `HtmlElement`](../web_sys.md) เพื่อเรียนรู้เกี่ยวกับการใช้งาน `leptos::HtmlElement` และดูตัวอย่าง CodeSandbox ฉบับเต็มได้ที่ท้ายหน้านี้

## กรณีพิเศษ: `<textarea>` และ `<select>`

เอลิเมนต์ฟอร์มสองตัวนี้มักสร้างความสับสนเนื่องจากมีพฤติกรรมเฉพาะตัว:

### `<textarea>`

ต่างจาก `<input>` เอลิเมนต์ `<textarea>` ไม่รองรับแอตทริบิวต์ `value` ในมาตรฐาน HTML แต่จะรับค่าเริ่มต้นเป็นโหนดข้อความธรรมดาที่อยู่ภายในแท็ก (เป็น child node) แทน

ดังนั้น ถ้าคุณต้องการให้เซิร์ฟเวอร์เรนเดอร์ค่าเริ่มต้น และให้ค่านั้นตอบสนองแบบรีแอกทีฟในเบราว์เซอร์ด้วย คุณสามารถทำทั้งสองอย่างพร้อมกันได้ คือส่งโหนดข้อความเริ่มต้นเป็น child พร้อมกับใช้ `prop:value` เพื่อกำหนดค่าปัจจุบันของมันใน DOM

```rust
view! {
    <textarea
        prop:value=move || some_value.get()
        on:input:target=move |ev| some_value.set(ev.target().value())
    >
        {some_value}
    </textarea>
}
```

### `<select>`

เอลิเมนต์ `<select>` ก็สามารถควบคุมได้ในทำนองเดียวกันผ่านพร็อพเพอร์ตี `value` บนตัว `<select>` เอง ซึ่งจะเลือก `<option>` ที่มีค่านั้นให้โดยอัตโนมัติ

```rust
let (value, set_value) = signal(0i32);
view! {
  <select
    on:change:target=move |ev| {
      set_value.set(ev.target().value().parse().unwrap());
    }
    prop:value=move || value.get().to_string()
  >
    <option value="0">"0"</option>
    <option value="1">"1"</option>
    <option value="2">"2"</option>
  </select>
  // a button that will cycle through the options
  <button on:click=move |_| set_value.update(|n| {
    if *n == 2 {
      *n = 0;
    } else {
      *n += 1;
    }
  })>
    "Next Option"
  </button>
}
```

```admonish sandbox title="ฟอร์มแบบควบคุมเทียบกับแบบไม่ควบคุมบน CodeSandbox" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/5-forms-0-7-l5hktg?file=%2Fsrc%2Fmain.rs&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/5-forms-0-7-l5hktg?file=%2Fsrc%2Fmain.rs&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::{ev::SubmitEvent};
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    view! {
        <h2>"Controlled Component"</h2>
        <ControlledComponent/>
        <h2>"Uncontrolled Component"</h2>
        <UncontrolledComponent/>
    }
}

#[component]
fn ControlledComponent() -> impl IntoView {
    // create a signal to hold the value
    let (name, set_name) = signal("Controlled".to_string());

    view! {
        <input type="text"
            // fire an event whenever the input changes
            // adding :target after the event gives us access to
            // a correctly-typed element at ev.target()
            on:input:target=move |ev| {
                set_name.set(ev.target().value());
            }

            // the `prop:` syntax lets you update a DOM property,
            // rather than an attribute.
            //
            // IMPORTANT: the `value` *attribute* only sets the
            // initial value, until you have made a change.
            // The `value` *property* sets the current value.
            // This is a quirk of the DOM; I didn't invent it.
            // Other frameworks gloss this over; I think it's
            // more important to give you access to the browser
            // as it really works.
            //
            // tl;dr: use prop:value for form inputs
            prop:value=name
        />
        <p>"Name is: " {name}</p>
    }
}

#[component]
fn UncontrolledComponent() -> impl IntoView {
    // import the type for <input>
    use leptos::html::Input;

    let (name, set_name) = signal("Uncontrolled".to_string());

    // we'll use a NodeRef to store a reference to the input element
    // this will be filled when the element is created
    let input_element: NodeRef<Input> = NodeRef::new();

    // fires when the form `submit` event happens
    // this will store the value of the <input> in our signal
    let on_submit = move |ev: SubmitEvent| {
        // stop the page from reloading!
        ev.prevent_default();

        // here, we'll extract the value from the input
        let value = input_element.get()
            // event handlers can only fire after the view
            // is mounted to the DOM, so the `NodeRef` will be `Some`
            .expect("<input> to exist")
            // `NodeRef` implements `Deref` for the DOM element type
            // this means we can call`HtmlInputElement::value()`
            // to get the current value of the input
            .value();
        set_name.set(value);
    };

    view! {
        <form on:submit=on_submit>
            <input type="text"
                // here, we use the `value` *attribute* to set only
                // the initial value, letting the browser maintain
                // the state after that
                value=name

                // store a reference to this input in `input_element`
                node_ref=input_element
            />
            <input type="submit" value="Submit"/>
        </form>
        <p>"Name is: " {name}</p>
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
</preview>
