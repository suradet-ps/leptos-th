# `<ActionForm/>`

[`<ActionForm/>`](https://docs.rs/leptos/latest/leptos/form/fn.ActionForm.html) เป็น `<Form/>` เฉพาะทางที่รับแอ็กชันฝั่งเซิร์ฟเวอร์ และส่งมันโดยอัตโนมัติเมื่อส่งฟอร์ม สิ่งนี้ช่วยให้คุณเรียกฟังก์ชันฝั่งเซิร์ฟเวอร์ได้โดยตรงจาก `<form>` แม้ไม่มี JS/WASM

ขั้นตอนนั้นง่ายมาก:

1. นิยามฟังก์ชันฝั่งเซิร์ฟเวอร์โดยใช้[มาโคร `#[server]`](https://docs.rs/leptos/latest/leptos/attr.server.html) (ดู[ฟังก์ชันฝั่งเซิร์ฟเวอร์](../server/25_server_functions.md))
2. สร้างแอ็กชันโดยใช้ [`ServerAction::new()`](https://docs.rs/leptos/latest/leptos/server/struct.ServerAction.html) โดยระบุชนิดของฟังก์ชันฝั่งเซิร์ฟเวอร์ที่คุณนิยามไว้
3. สร้าง `<ActionForm/>` โดยส่งแอ็กชันฝั่งเซิร์ฟเวอร์ผ่านพร็อพ `action`
4. ส่งอาร์กิวเมนต์แบบมีชื่อของฟังก์ชันฝั่งเซิร์ฟเวอร์เป็นฟิลด์ฟอร์มที่มีชื่อเดียวกัน

> **หมายเหตุ:** `<ActionForm/>` ทำงานได้เฉพาะกับการเข้ารหัส `POST` แบบ URL-encoded ซึ่งเป็นค่าเริ่มต้นสำหรับฟังก์ชันฝั่งเซิร์ฟเวอร์ เพื่อให้มั่นใจว่าลดทอนอย่างสง่างาม/ทำงานถูกต้องในฐานะฟอร์ม HTML

```rust
#[server]
pub async fn add_todo(title: String) -> Result<(), ServerFnError> {
    todo!()
}

#[component]
fn AddTodo() -> impl IntoView {
    let add_todo = ServerAction::<AddTodo>::new();
    // holds the latest *returned* value from the server
    let value = add_todo.value();
    // check if the server has returned an error
    let has_error = move || value.with(|val| matches!(val, Some(Err(_))));

    view! {
        <ActionForm action=add_todo>
            <label>
                "Add a Todo"
                // `title` matches the `title` argument to `add_todo`
                <input type="text" name="title"/>
            </label>
            <input type="submit" value="Add"/>
        </ActionForm>
    }
}
```

ง่ายจริงๆ นั่นแหละ เมื่อมี JS/WASM ฟอร์มของคุณจะส่งโดยไม่รีโหลดหน้าเพจ โดยเก็บการส่งครั้งล่าสุดไว้ในสัญญาณ `.input()` ของแอ็กชัน สถานะที่กำลังดำเนินการไว้ใน `.pending()` และอื่นๆ (ดูเอกสารของ [`Action`](https://docs.rs/leptos/latest/leptos/reactive/actions/struct.Action.html) เพื่อทบทวนหากต้องการ) เมื่อไม่มี JS/WASM ฟอร์มของคุณจะส่งพร้อมกับการรีโหลดหน้าเพจ หากคุณเรียกฟังก์ชัน `redirect` (จาก `leptos_axum` หรือ `leptos_actix`) มันจะเปลี่ยนเส้นทางไปยังหน้าที่ถูกต้อง ตามค่าเริ่มต้น มันจะเปลี่ยนเส้นทางกลับมาที่หน้าเพจที่คุณอยู่ปัจจุบัน พลังของ HTML, HTTP และการเรนเดอร์แบบไอโซมอร์ฟิกทำให้ `<ActionForm/>` ของคุณทำงานได้เลย แม้ไม่มี JS/WASM

## การตรวจสอบความถูกต้องฝั่งไคลเอนต์

เนื่องจาก `<ActionForm/>` ก็เป็นแค่ `<form>` มันจึงยิงเหตุการณ์ `submit` คุณจะใช้การตรวจสอบความถูกต้องของ HTML หรือใช้ลอจิกการตรวจสอบฝั่งไคลเอนต์ของคุณเองในตัวจัดการเหตุการณ์ `on:submit:capture` ก็ได้ เพียงเรียก `ev.prevent_default()` เพื่อยับยั้งการส่งฟอร์ม

แทรต [`FromFormData`](https://docs.rs/leptos/latest/leptos/form/trait.FromFormData.html) อาจมีประโยชน์ตรงนี้ สำหรับการพยายามพาร์สชนิดข้อมูลของฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณจากฟอร์มที่ถูกส่งมา

```rust
let on_submit = move |ev| {
	let data = AddTodo::from_event(&ev);
	// silly example of validation: if the todo is "nope!", nope it
	if data.is_err() || data.unwrap().title == "nope!" {
		// ev.prevent_default() will prevent form submission
		ev.prevent_default();
	}
}

// ... add the `submit` handler to an `ActionForm`

<ActionForm on:submit:capture=on_submit /* ... */>
```

```admonish note
สังเกตว่าเราใช้ `on:submit:capture` แทน `on:submit` นี่จะเพิ่มตัวรับฟังเหตุการณ์ที่จะทำงานในเฟส “capture” ของการจัดการเหตุการณ์ในเบราว์เซอร์ แทนที่จะเป็นเฟส “bubble” ซึ่งหมายความว่าตัวจัดการเหตุการณ์ของคุณจะรันก่อนตัวจัดการ `submit` ที่มีมาให้ในตัวของ `ActionForm` หากต้องการข้อมูลเพิ่มเติม ดูได้ที่ [issue นี้](https://github.com/leptos-rs/leptos/issues/3872)
```

## อินพุตที่ซับซ้อน

อาร์กิวเมนต์ของฟังก์ชันฝั่งเซิร์ฟเวอร์ที่เป็นสตรักต์ซึ่งมีฟิลด์ที่สามารถซีเรียลไลซ์ได้ซ้อนอยู่ภายใน ควรใช้สัญกรณ์การทำดัชนีของ `serde_qs`

```rust
#[derive(serde::Serialize, serde::Deserialize, Debug, Clone)]
struct Settings {
    display_name: String,
}

#[derive(serde::Serialize, serde::Deserialize, Debug, Clone)]
struct HeftyData {
    first_name: String,
    last_name: String,
    settings: Settings,
}

#[component]
fn ComplexInput() -> impl IntoView {
    let submit = ServerAction::<VeryImportantFn>::new();

    view! {
      <ActionForm action=submit>
        <input type="text" name="hefty_arg[first_name]" value="leptos"/>
        <input
          type="text"
          name="hefty_arg[last_name]"
          value="closures-everywhere"
        />
        <input
          type="text"
          name="hefty_arg[settings][display_name]"
          value="my alias"
        />
        <input type="submit"/>
      </ActionForm>
    }
}

#[server]
async fn very_important_fn(hefty_arg: HeftyData) -> Result<(), ServerFnError> {
    assert_eq!(hefty_arg.first_name.as_str(), "leptos");
    assert_eq!(hefty_arg.last_name.as_str(), "closures-everywhere");
    aseert_eq!(hefty_arg.settings.display_name.as_str(), "my alias");
    Ok(())
}
```
